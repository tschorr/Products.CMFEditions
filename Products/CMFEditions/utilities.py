#########################################################################
# Copyright (c) 2004, 2005 Alberto Berti, Gregoire Weber.
# All Rights Reserved.
#
# This file is part of CMFEditions.
#
# CMFEditions is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CMFEditions is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CMFEditions; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#########################################################################
"""Utilities

$Id: utilities.py,v 1.1 2005/01/06 14:25:44 gregweb Exp $
"""

import random

from Persistence import Persistent
from Acquisition import aq_base
from OFS.CopySupport import CopySource
from Products.CMFCore.utils import getToolByName

STUB_OBJECT_PREFIX = '_CMFEditionsTempId'

class KwAsAttributes(Persistent):
    """Class attaching to itself passed keyword attributes.
    """
    def __init__(self, **kw):
        for key, val in kw.items():
            setattr(self, key, val)


def dereference(obj=None, history_id=None, zodb_hook=None):
    """Dereference an object.

    Works with either an obj or a history_id or both.

    If only a history_id is used, then a 'zodb_hook' is required to obtain
    the uid tool.

    Returns a tuple consisting of the derefrenced object and
    the unique id of the object: ``(obj, uid)``

    If an object or history_id cannot be found None will be returned for
    one or both values.
    """

    if zodb_hook is None:
        # try to use the reference as zodb hook
        zodb_hook = obj

    portal_uidhandler = getToolByName(zodb_hook, 'portal_uidhandler')

    if history_id is None:
        if obj is None:
            raise TypeError, "This method requires either an obj or a history_id"
        else:
            history_id = portal_uidhandler.queryUid(obj, None)
    elif obj is None:
        try:
            obj = portal_uidhandler.queryObject(history_id, None)
        except AttributeError:
            # We may get an attribute error in some cases, just return None
            pass

    return obj, history_id


def generateId(parent, prefix='', volatile=False):
    """Generate an unused id (optionaly a volatile one).
    """
    existingIds = parent.objectIds()
    idTemplate = '%s%s_%%s' % (volatile * '__v_', prefix + STUB_OBJECT_PREFIX)
    while 1:
        id =  idTemplate % random.randrange(1000000)
        if id not in existingIds:
            return id


def wrap(obj, parent):
    """Copy the context and containment from one object to another.

    This is needed to allow acquiring attributes. Containment and context
    is setup only in direction to the parents but not from the parent
    to itself. So doing the following raises an ``AttributeError``::

        getattr(wrapped.aq_parent, tempAttribute)
    """
    # be sure the obj is unwraped before wrapping it (argh, having
    # caused pulling my hair out until I realized it is wrapped)
    obj = aq_base(obj).__of__(parent)

    # set containment temporarly
    tempAttribute = generateId(parent, volatile=True)
    changed = parent._p_changed
    setattr(parent, tempAttribute, obj)
    wrapped = getattr(parent, tempAttribute)
    delattr(parent, tempAttribute)
    parent._p_changed = changed

    return wrapped
