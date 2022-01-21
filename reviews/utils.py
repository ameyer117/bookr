from statistics import mean


def average_rating(rating_list):
    if not rating_list:
        return 0

    return mean(rating_list)