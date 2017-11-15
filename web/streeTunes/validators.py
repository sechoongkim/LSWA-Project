from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def validate_length(value, length):
    if len(value) != length:
        raise ValidationError(
            _('%(value)s is not of length %(length)s number'),
            params={'value': value, 'length':length},
        )
        pass
    pass

