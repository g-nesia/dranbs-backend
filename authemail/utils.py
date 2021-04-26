from django.contrib.auth import get_user_model


def make_username(first_name, last_name):
    User = get_user_model()
    first_name = first_name.lower()
    last_name = last_name.lower()
    initial_username = "{}.{}".format(first_name, last_name)
    same_username_count = User.objects.filter(username=initial_username).count()
    if same_username_count > 0:
        username = "{}.{}".format(initial_username, same_username_count)
    else:
        username = initial_username
    return username
