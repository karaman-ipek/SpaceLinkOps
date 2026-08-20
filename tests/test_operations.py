import pytest

from spacelinkops.operations import *


def authority():
    return CommandAuthority([CommandDefinition("SET_HEATER",False,("NOMINAL",),{"level":(0,100)}),CommandDefinition("DEPLOY",True,("NOMINAL",),{})])
def users():return User("op",Role.OPERATOR),User("a1",Role.APPROVER),User("a2",Role.APPROVER),User("fd",Role.FLIGHT_DIRECTOR)
def test_inhibit_blocks_release():
    a=authority();op,a1,_,fd=users();c=a.submit(op,"SET_HEATER",{"level":25},"NOMINAL");a.approve(a1,c.command_id);a.set_inhibit(fd,True,"test")
    with pytest.raises(RuntimeError):a.release(fd,c.command_id,"NOMINAL")
def test_hazardous_dual_control():
    a=authority();op,a1,a2,fd=users();c=a.submit(op,"DEPLOY",{},"NOMINAL");a.approve(a1,c.command_id)
    with pytest.raises(RuntimeError):a.release(fd,c.command_id,"NOMINAL")
    a.approve(a2,c.command_id);assert a.release(fd,c.command_id,"NOMINAL").state=="RELEASED_TO_SIMULATOR"
def test_submitter_cannot_approve():
    a=authority();fd=users()[-1];c=a.submit(fd,"DEPLOY",{},"NOMINAL")
    with pytest.raises(ValueError):a.approve(fd,c.command_id)
def test_release_is_simulator_only():
    a=authority();op,a1,_,fd=users();c=a.submit(op,"SET_HEATER",{"level":10},"NOMINAL");a.approve(a1,c.command_id);a.release(fd,c.command_id,"NOMINAL");assert a.audit.export()[-1]["details"]["offline_only"] is True
