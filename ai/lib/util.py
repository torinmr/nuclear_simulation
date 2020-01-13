from lib.location import Location

def can_intercept(missile, start_location, speed, max_range):
    """Determine if a missile can be intercepted.
    
    Args:
      missile: Missile to intercept.
      start_location: Location interceptors are fired from.
      speed: Speed of interceptors, in km/s.
      max_range: Maximum interceptor range, in km.
    Returns:
      The number of seconds (rounded up) before the missile
      can be intercepted, or None if it can't be intercepted.
    """
    max_time = int(max_range / speed)
    missile_location = missile.location
    interceptor_range = 0.0
    
    interception_time = None
    
    # Before doing the loop below, see if it is completely outside of our range.
    distance_to_missile = start_location.distance_to(missile_location)
    missile_max_range = missile.speed * (max_time + 1)
    interceptor_max_range = speed * (max_time + 1)

    # If the interceptor and missile couldn't hit each other even if they flew
    # directly towards each other, then there's no point in doing the detailed
    # check.
    if missile_max_range + interceptor_max_range > distance_to_missile:
        for t in range(1, max_time + 1):
            missile_location = missile_location.move_towards(
                missile.target.location, missile.speed)
            interceptor_range += speed
            if start_location.distance_to(missile_location) < interceptor_range:
                interception_time = t
                break

    return interception_time


def launch_missile_salvo(s, time, launchers, target_dict):
    """Launch a bunch of missiles at a bunch of targets.
    
    Args:
      s: Simulation object.
      time: Time to launch the salvo.
      launchers: A list of launchers to launch from.
      target_dict: A dict mapping target objects to missile counts. The total number
                   of missiles must be less than or equal to the length of launchers.
    """
    launcher_index = 0
    for target, num_missiles in target_dict.items():
        for _ in range(num_missiles):
            if launcher_index >= len(launchers):
                raise ValueError("Not enough launchers!")

            launcher = launchers[launcher_index]
            launcher_index += 1
            
            s.schedule_event(time, lambda t, launcher=launcher, target=target:
                             launcher.launch_missile(t, target))
            
def find_entity_by_name(entity_list, name):
    for entity in entity_list:
        if entity.name == name:
            return entity
    raise KeyError("No entity with the name {}.".format(name))
