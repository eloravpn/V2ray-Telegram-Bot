big_range = list(range(512))


class CallbackActions:
    ADD, REMOVE, REGISTER, GET_USERS, GET_ACCOUNTS, *rest = (
        big_range
    )
