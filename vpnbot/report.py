import datetime

from logzero import logger as log

from vpnbot import appglobals
from vpnbot.models import Account, AccountTraffic
from vpnbot.xui import get_all_client_infos
from logzero import logger as log


def save_current_accounts_traffic():
    client_list = get_all_client_infos(appglobals.V2RAY_INBOUND_ID, -1, -1, enabled=True)

    for index, client in enumerate(client_list):
        try:
            account = Account.by_email(client['email'])
            account_traffic = AccountTraffic(account=account, total=client['total'],
                                             download=client['down'], upload=client['up'])
            account_traffic.save()

        except Account.DoesNotExist:
            log.error("Account does not exist with email: " + client['email'])


def get_all_accounts_usage(day: int = 1):
    today = datetime.datetime.now()
    n_days_ago = today - datetime.timedelta(days=day)

    log.info('Generate report from ' + str(n_days_ago))

    report = []

    accounts_ids = Account.select(Account.id).join(AccountTraffic).where(
        AccountTraffic.date_added >= n_days_ago).distinct()

    for account_id in accounts_ids:
        account = Account.select().where(Account.id == account_id).get()
        accounts_traffics = AccountTraffic.select().where(
            (AccountTraffic.account == account) & (AccountTraffic.date_added >= n_days_ago)).order_by(
            AccountTraffic.date_added.desc())

        if accounts_traffics:
            total = accounts_traffics[0].total
            upload = accounts_traffics[0].upload - accounts_traffics[-1].upload
            download = accounts_traffics[0].download - accounts_traffics[-1].download

            if upload < 0 or download < 0:
                log.error(f"{account.user.markdown_short} Wrong Report Download: {download} Upload: {upload}")
                continue

            usage = {'account_id': account_id,
                     'upload': upload,
                     'download': download,
                     'total': total}
            report.append(usage)
        else:
            print('No Accounts Traffic for ' + str(account.id))
    return report


def get_top_accounts_usage(day: int = 1, top: int = 10):
    top_accounts_usage = get_all_accounts_usage(day)
    top_accounts_usage.sort(reverse=True, key=lambda item: item['upload'] + item['download'])
    return top_accounts_usage[:top]


def get_sum_accounts_usage(day: int = 1):
    top_accounts_usage = get_all_accounts_usage(day)
    return sum(item['upload'] + item['download'] for item in top_accounts_usage)
