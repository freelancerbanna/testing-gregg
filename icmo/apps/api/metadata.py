from collections import OrderedDict, defaultdict

from rest_framework.metadata import SimpleMetadata


class KendoUIMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super(KendoUIMetadata, self).determine_metadata(request, view)
        if 'actions' in metadata and 'POST' in metadata['actions']:
            fields = defaultdict(dict)
            for field_name, action in metadata['actions']['POST'].items():
                fields[field_name] = {}
                if action['read_only']:
                    fields[field_name]['editable'] = False
                if action['required']:
                    fields[field_name]['required'] = True
                    fields[field_name]['validation'] = dict(required=True)

                if action['type'] == 'url':
                    fields[field_name]['validation'] = dict(url=True)
                if action['type'] == 'email':
                    fields[field_name]['validation'] = dict(email=True)

                action['original_type'] = action['type']
                if action['type'] in ('date', 'datetime'):
                    fields[field_name]['type'] = 'date'
                elif action['type'] in ('integer', 'float', 'decimal'):
                    fields[field_name]['type'] = 'number'
                elif action['type'] != 'boolean':
                    fields[field_name]['type'] = 'string'

            fields = OrderedDict(sorted(fields.items()))
            metadata['kendoUI'] = dict(
                idField='slug' if 'slug' in fields else 'id',
                id='slug' if 'slug' in fields else 'id',
                fields=fields
            )
        return metadata

    def get_field_info(self, field):
        field_info = super(KendoUIMetadata, self).get_field_info(field)
        return field_info

