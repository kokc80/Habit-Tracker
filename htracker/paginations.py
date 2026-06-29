from rest_framework.pagination import LimitOffsetPagination


class ViewUserHabitPagination(LimitOffsetPagination):
    """
    Пагинация при выводе привычек
    """
    default_limit = 20
    limit_query_param = 'l'
    offset_query_param = 'o'
    max_limit = 100