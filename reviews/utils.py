from statistics import mean


def average_rating(rating_list):
    if not rating_list:
        return 0

    return mean(rating_list)


def build_search_history(current_history, new_search):
    if new_search in current_history:
        current_history.remove(new_search)

    current_history.insert(0, new_search)

    return current_history[:10]
