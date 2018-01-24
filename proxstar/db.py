import datetime
from sqlalchemy import exists
from dateutil.relativedelta import relativedelta
from proxstar.ldapdb import *
from proxstar.models import VM_Expiration, Usage_Limit, Base


def get_vm_expire(db, vmid, months):
    if db.query(exists().where(VM_Expiration.id == vmid)).scalar():
        expire = db.query(VM_Expiration).filter(
            VM_Expiration.id == vmid).one().expire_date
    else:
        expire = datetime.date.today() + relativedelta(months=months)
        new_expire = VM_Expiration(id=vmid, expire_date=expire)
        db.add(new_expire)
        db.commit()
    return expire


def renew_vm_expire(db, vmid, months):
    if db.query(exists().where(VM_Expiration.id == vmid)).scalar():
        expire = db.query(VM_Expiration).filter(VM_Expiration.id == vmid).one()
        new_expire = datetime.date.today() + relativedelta(months=months)
        expire.expire_date = new_expire
        db.commit()
    else:
        expire = datetime.date.today() + relativedelta(months=months)
        new_expire = VM_Expiration(id=vmid, expire_date=expire)
        db.add(new_expire)
        db.commit()


def delete_vm_expire(db, vmid):
    if db.query(exists().where(VM_Expiration.id == vmid)).scalar():
        expire = db.query(VM_Expiration).filter(VM_Expiration.id == vmid).one()
        db.delete(expire)
        db.commit()


def get_expired_vms(db):
    expired = []
    today = datetime.date.today().strftime('%Y-%m-%d')
    expire = db.query(VM_Expiration).filter(
        VM_Expiration.expire_date < today).all()
    for vm in expire:
        expired.append(vm.id)
    return expired


def get_user_usage_limits(db, user):
    limits = dict()
    if is_rtp(user):
        limits['cpu'] = 1000
        limits['mem'] = 1000
        limits['disk'] = 100000
    elif db.query(exists().where(Usage_Limit.id == user)).scalar():
        limits['cpu'] = db.query(Usage_Limit).filter(
            Usage_Limit.id == user).one().cpu
        limits['mem'] = db.query(Usage_Limit).filter(
            Usage_Limit.id == user).one().mem
        limits['disk'] = db.query(Usage_Limit).filter(
            Usage_Limit.id == user).one().disk
    else:
        limits['cpu'] = 4
        limits['mem'] = 4
        limits['disk'] = 100
    return limits


def set_user_usage_limits(db, user, cpu, mem, disk):
    if db.query(exists().where(Usage_Limit.id == user)).scalar():
        limits = db.query(Usage_Limit).filter(Usage_Limit.id == user).one()
        limits.cpu = cpu
        limits.mem = mem
        limits.disk = disk
        db.commit()
    else:
        limits = Usage_Limit(id=user, cpu=cpu, mem=mem, disk=disk)
        db.add(limits)
        db.commit()


def delete_user_usage_limits(db, user):
    if db.query(exists().where(Usage_Limit.id == user)).scalar():
        limits = db.query(Usage_Limit).filter(Usage_Limit.id == user).one()
        db.delete(limits)
        db.commit()