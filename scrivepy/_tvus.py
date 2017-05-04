from datetime import datetime
import re

from dateutil.tz import tzutc
from tvu import TVU


class IDTVU(TVU):

    TYPES = unicode,

    def validate(self, value):
        if not re.search(r'^[0-9]+$', value):
            self.error(u'non-empty digit-string')


class TimeTVU(TVU):

    TYPES = datetime, unicode

    def unify(self, value):
        if isinstance(value, unicode):
            try:
                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
                return value.replace(tzinfo=tzutc())
            except ValueError:
                self.error(u'time string', soft=True)
        return value
