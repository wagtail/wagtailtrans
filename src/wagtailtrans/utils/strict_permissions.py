def is_privileged_user(user_group_names: list):
    """
    Checks if a privileged user group name exist in a given list of group names.
    :param user_group_names: A list of group names.
    """
    privileged_roles = ['Moderators', 'Editors']
    if [item for item in privileged_roles if item in user_group_names]:
        return True
    return False


def allowed_language_codes(user_group_names: list):
    """
    Creates a list of allowed language codes from a user's group list.
    Assumes that translator groups use this naming pattern: `translator-{language code}`
    :param user_group_names: A list of group names.
    :return: A list of language codes as strings.
    """
    return [name.split('-')[-1] for name in user_group_names]
