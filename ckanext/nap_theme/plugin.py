import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base
import ckan.lib.navl.dictization_functions as df
import re
import datetime
from ckan.common import _
from flask import Blueprint
from ckan import logic
from urllib.request import urlopen, URLError
from flask.templating import render_template

Invalid = df.Invalid

# custom templates - Not working :(
def cookies():
    return render_template(u'cookies.html')

# helper functions
def get_extra(package_extras, key):
    ''' Used for getting a specific package extras

    :param package_extras: the package extras
    :type package_extras: dict
    '''
    for extra in package_extras:
        if key == extra['key']:
            return extra['value']
            break
    return None
    
def get_orgs():
    orgs = logic.get_action('organization_list')({}, {'all_fields': 'true'})
    return orgs

def get_tags():
    tags = logic.get_action('tag_list')({}, {'all_fields': 'true'})
    return tags

def get_tag_names(package_tags):
    tag_names = ','.join([tag['display_name'] for tag in package_tags])
    return tag_names

def get_sorted_error_summary(errorsDict):
    if errorsDict:
        # Sorted error summary message so they appear in the right order and strip off sorted order added in the custom validators
        sortedErrors = sorted(errorsDict.items(), key=lambda value: value[1] )
        sortedErrorsDict = dict(sortedErrors)
        # remove sorting number
        for k,v in sortedErrorsDict.items():
            sortedErrorsDict[k] = v.split('|')[1]
        return sortedErrorsDict
    else:
        return {}

def get_form_data(form_data, pkg_dict):
    #    Set initial value for all form values required
    blank_form_dict = {
        'owner_org' : '',
        'title' : '',
        'notes' : '',
        'url': 'http://',
        'tag_string': '',
        'license_id' : '',
        'version': '',
        'author': '',
        'author_email': '',
        'data_formats': '',
        'update_frequency': '',
        'location' : '',
        'regularly_updated': '',
        'date_range_latest': '',
        'date_range_earliest': '',
        'date_range_earliest_day': '',
        'date_range_earliest_month': '',
        'date_range_earliest_year': '',
        'date_range_latest_day': '',
        'date_range_latest_month': '',
        'date_range_latest_year': '',
        'regularly_updated_earliest_day': '',
        'regularly_updated_earliest_month': '',
        'regularly_updated_earliest_year': '',
        'description': '',
        'data_available': '',
    }
    # set value of form either blank if new, edit value or if an error the value entered by the user!
    for key in blank_form_dict.keys():
        if not key in form_data:
            if key in pkg_dict:
                # special case handling for tags!
                if (key == 'tag_string'):
                    form_data[key] = get_tag_names(pkg_dict.tags)
                else:
                    form_data[key] = pkg_dict[key]
            else:
                form_data[key] = blank_form_dict[key]
    form_data['date_range_earliest'] = f"{form_data['date_range_earliest_day']}/{form_data['date_range_earliest_month']}/{form_data['date_range_earliest_year']}"
    form_data['date_range_latest'] = f"{form_data['date_range_latest_day']}/{form_data['date_range_latest_month']}/{form_data['date_range_latest_year']}"
    return form_data

def get_package_display_name(display_name):
    if display_name == 'Dataset':
        display_name = 'Transport Data'
    return display_name

# Custom validators
def custom_url_validator(key, data, errors, context):
    data_available = data.get(('data_available',))
    if data_available == "yes":
        ''' Checks that the provided value is a valid URL and exists!'''
        url = data.get(key, None)
        try:
            urlopen(url)
            return
        except URLError:
            raise Invalid(_('2|Enter a dataset link URL that exists.'))
        except: 
            raise Invalid(_('2|Enter a dataset link that is a correct URL, like https://data.gov.uk/'))
            

def custom_owner_org_validator(key, data, errors, context):
    value = data.get(key)
    if value == '':
        raise Invalid(_('1|Select a publisher'))

def custom_title_validator(key, data, errors, context):
    value = data.get(key)
    if value == '':
        raise Invalid(_('2|Enter a title'))

def custom_author_email_validator(value, context):
    email_pattern = re.compile(
                            # additional pattern to reject malformed dots usage
                            r"^(?!\.)(?!.*\.$)(?!.*?\.\.)"\
                            "[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9]"\
                            "(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"\
                            "(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
                        )
    # validate email input 
    if value:
        if not email_pattern.match(value):
            raise Invalid(_('5|Enter a contact email in the correct format, like name@test.com'))
    return value

def custom_location_validator(key, data, errors, context):
    value = data.get(key)
    if value == '':
        raise Invalid(_('3|Enter a what location does this dataset cover'))

def custom_update_frequency_validator(key, data, errors, context):
    is_updated = data.get(('regularly_updated',))
    value = data.get(key)
    if is_updated == 'yes':
        if value == '':
            raise Invalid(_('4|Enter the frequency of update of the dataset'))
    return value

def custom_description_validator(key, data, errors, context):
    value = data.get(key)
    if value == '':
        raise Invalid(_('5|Enter what this dataset measures'))

def custom_date_range_earliest_validator(key, data, errors, context):
    is_updated = data.get(('regularly_updated',))
    if is_updated == 'no':
        year = data.get(('date_range_earliest_year',))
        month = data.get(('date_range_earliest_month',))
        day = data.get(('date_range_earliest_day',))

        if year and month and year:
            try:
                date = datetime.datetime(int(year), int(month), int(day))
            except:
                 raise Invalid(_('6|Earliest date must be a real date'))
            now = datetime.datetime.now()
            if date > now:
                raise Invalid(_('6|Enter a earliest date that is in the past'))

def custom_date_range_latest_validator(key, data, errors, context):
    is_updated = data.get(('regularly_updated',))
    if is_updated == 'no':
        year = data.get(('date_range_latest_year',))
        month = data.get(('date_range_latest_month',))
        day = data.get(('date_range_latest_day',))

        if year and month and year:
            try:
                date = datetime.datetime(int(year), int(month), int(day))
            except:
                raise Invalid(_('5|Latest date must be a real date'))
            now = datetime.datetime.now()
            if date > now:
                raise Invalid(_('5|Enter a latest date that is in the past'))
            earliest_year = data.get(('date_range_earliest_year',))
            earliest_month = data.get(('date_range_earliest_month',))
            earliest_day = data.get(('date_range_earliest_day',))
            _custom_date_range_validator(year, month, day, earliest_year, earliest_month, earliest_day)

def _custom_date_range_validator(latest_year, latest_month, latest_day, earliest_year, earliest_month, earliest_day):
    now = datetime.datetime.now()
    if latest_year and latest_month and latest_year and earliest_year and earliest_month and earliest_day:
        try:
            latest_date = datetime.datetime(int(latest_year), int(latest_month), int(latest_day))
            earliest_date = datetime.datetime(int(earliest_year), int(earliest_month), int(earliest_day))
        except: 
            return
        if earliest_date > latest_date:
            raise Invalid(_('6|Enter a latest date that is after the earliest date'))

def _custom_date_field_validator(data, key):
    is_updated = data.get(('regularly_updated',))
    if is_updated == 'no':
        date = data.get(key)
        return (date == '')
    return False

def custom_latest_year_validator(key, data, errors, context):
    if _custom_date_field_validator(data, key):
        raise Invalid(_('8|The latest date must include a year'))

def custom_latest_month_validator(key, data, errors, context):
    if _custom_date_field_validator(data, key):
        raise Invalid(_('8|The latest date must include a month'))

def custom_latest_day_validator(key, data, errors, context):
    if _custom_date_field_validator(data, key):
        raise Invalid(_('8|The latest date must include a day'))

def custom_earliest_year_validator(key, data, errors, context):
    if _custom_date_field_validator(data, key):
        raise Invalid(_('9|The earliest date must include a year'))

def custom_earliest_month_validator(key, data, errors, context):
    if _custom_date_field_validator(data, key):
        raise Invalid(_('9|The earliest date must include a month'))

def custom_earliest_day_validator(key, data, errors, context):
    if _custom_date_field_validator(data, key):
        raise Invalid(_('9|The earliest date must include a day'))

def custom_regularly_updated_validatior(value):
    if not value:
        raise Invalid(_('7|Enter if this dataset is updated regularly'))
    return value

def custom_data_available_validator(value):
    if not value:
        raise Invalid(_('6|Enter if this dataset is available'))
    return value

def custom_required_author_email_validator(key, data, errors, context):
    data_available = data.get(('data_available',))
    value = data.get(key)
    if data_available == "no" and not value:
        raise Invalid(_('9|Enter contact email for people to request the dataset'))
    return value

def custom_required_author_name_validator(key, data, errors, context):
    data_available = data.get(('data_available',))
    value = data.get(key)
    if data_available == "no" and not value:
        raise Invalid(_('8|Enter contact name for people to request the dataset'))
    return value



class NapThemePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IValidators)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'fanstatic')
        toolkit.add_resource('fanstatic',
            'nap_theme')

    # ITemplateHelpers 
    def get_helpers(self):
        return {
            'nap_theme_get_extra': get_extra, 
            'nap_theme_get_orgs': get_orgs, 
            'nap_theme_get_tags': get_tags,
            'nap_theme_get_tag_names': get_tag_names,
            'nap_theme_get_sorted_error_summary': get_sorted_error_summary,
            'nap_theme_get_form_data' : get_form_data,
            'nap_theme_get_package_display_name' : get_package_display_name
            }

    # IBlueprint
    def get_blueprint(self):
        u'''Return a Flask Blueprint object to be registered by the app.'''
        # Create Blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        # Add plugin url rules to Blueprint object
        blueprint.add_url_rule('/cookies', view_func=cookies)
        return blueprint

    # IPackageController
    def before_search(self, search_params):
        def make_filters_or(filter_query):
            from collections import defaultdict
            # fix issue with spaces in params such as tags we need to differentiate spaces between search terms and spaces
            filter_query = filter_query.replace('" ','"|||')
            filter_params = filter_query.split('|||')
            d = list(s.split(':') for s in filter_params)
            new_dict = defaultdict(list)
            for (key, value) in d:
                new_dict[key].append(value)
            filter_string = ""
            for (key, value) in new_dict.items():
                string = f'{key}:({" OR ".join(value)})'
                filter_string = filter_string + " " + string
            return filter_string

        if (search_params.get('fq', None) and not '+owner_org' in search_params['fq']):
            search_params["fq"] = make_filters_or(search_params['fq'])
        return search_params

    # Schema Changes
    def is_fallback(self):
       # Return True to register this plugin as the default handler for
       # package types not handled by any other IDatasetForm plugin.
       return True

    def package_types(self):
       # This plugin doesn't handle any special package types, it just
       # registers itself as the default (above).
       return []

    def create_package_schema(self):
 
       schema = super(NapThemePlugin, self).create_package_schema()
       schema = self._modify_package_schema(schema)

       return schema

    def update_package_schema(self):
       schema = super(NapThemePlugin, self).update_package_schema()
       schema = self._modify_package_schema(schema)
       return schema

    def _modify_package_schema(self, schema):
        schema.update({
            'url':[custom_url_validator,
                toolkit.get_converter('unicode_safe')],
            'title':[custom_title_validator,
                toolkit.get_converter('unicode_safe')],
            'author_email':[toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('unicode_safe'),
                custom_author_email_validator,
                custom_required_author_email_validator],
            'author':[toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('unicode_safe'),
                custom_required_author_name_validator],
            'name':[toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('unicode_safe')],
            'location':[custom_location_validator,
                toolkit.get_converter('convert_to_extras')],
            'data_formats':[toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')],
            'update_frequency':[custom_update_frequency_validator,
                toolkit.get_converter('convert_to_extras')],
            'regularly_updated':[custom_regularly_updated_validatior,
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')],
            'date_range_earliest_day': [custom_earliest_day_validator,
                toolkit.get_converter('convert_to_extras')],
            'date_range_earliest_month': [custom_earliest_month_validator,
                toolkit.get_converter('convert_to_extras')],
            'date_range_earliest_year': [custom_earliest_year_validator,
                toolkit.get_converter('convert_to_extras')],
            'date_range_latest_day': [custom_latest_day_validator,
                toolkit.get_converter('convert_to_extras')],
            'date_range_latest_month': [custom_latest_month_validator,
                toolkit.get_converter('convert_to_extras')],
            'date_range_latest_year': [custom_latest_year_validator,
                toolkit.get_converter('convert_to_extras')],
            'date_range_earliest': [custom_date_range_earliest_validator],
            'date_range_latest': [custom_date_range_latest_validator],
            'regularly_updated_earliest_day':[toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')],
            'regularly_updated_earliest_month':[toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')],
            'regularly_updated_earliest_year':[toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')],
            'description':[custom_description_validator,
            toolkit.get_converter('convert_to_extras')],
            'data_available':[custom_data_available_validator,
                toolkit.get_converter('convert_to_extras')],
        })
        return schema

    def show_package_schema(self):
        schema = super(NapThemePlugin, self).show_package_schema()

        schema.update({
            'url':[toolkit.get_converter('unicode_safe'),
                custom_url_validator],
            'title':[toolkit.get_converter('unicode_safe'),
                custom_title_validator],
            'author_email':[toolkit.get_converter('unicode_safe'),
                toolkit.get_validator('ignore_missing'),
                custom_author_email_validator,
                custom_required_author_email_validator],
            'author': [toolkit.get_converter('unicode_safe'),
                toolkit.get_validator('ignore_missing'),
                custom_required_author_name_validator],
            'name':[toolkit.get_converter('unicode_safe'),
                    toolkit.get_validator('ignore_missing')],
            'location':[toolkit.get_converter('convert_from_extras'),
                custom_location_validator],
            'data_formats':[toolkit.get_converter('unicode_safe'),
                    toolkit.get_validator('convert_from_extras')],
            'update_frequency':[toolkit.get_converter('unicode_safe'),
                    toolkit.get_validator('convert_from_extras')],
            'regularly_updated':[toolkit.get_converter('unicode_safe'),
                    toolkit.get_validator('ignore_missing'),
                    toolkit.get_converter('convert_from_extras')],
            'date_range_earliest_day': [toolkit.get_converter('unicode_safe'),
                    custom_earliest_day_validator,
                    toolkit.get_converter('convert_from_extras')],
            'date_range_earliest_month': [toolkit.get_converter('unicode_safe'),
                    custom_earliest_month_validator,
                    toolkit.get_converter('convert_from_extras')],
            'date_range_earliest_year': [toolkit.get_converter('unicode_safe'),
                    custom_earliest_year_validator,
                    toolkit.get_converter('convert_from_extras')],
            'date_range_latest_day': [toolkit.get_converter('unicode_safe'), 
                    custom_latest_day_validator,
                    toolkit.get_converter('convert_from_extras')],
            'date_range_latest_month': [toolkit.get_converter('unicode_safe'), 
                    custom_latest_month_validator,
                    toolkit.get_converter('convert_from_extras')],
            'date_range_latest_year': [toolkit.get_converter('unicode_safe'), 
                    custom_latest_year_validator,
                    toolkit.get_converter('convert_from_extras')],
            'regularly_updated_earliest_day':[toolkit.get_converter('unicode_safe'),
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_from_extras')],
            'regularly_updated_earliest_month':[toolkit.get_converter('unicode_safe'),
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_from_extras')],
            'regularly_updated_earliest_year':[toolkit.get_converter('unicode_safe'),
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_from_extras')],
            'description':[custom_description_validator, 
                    toolkit.get_converter('convert_from_extras')],
            'data_available':[custom_data_available_validator,
                    toolkit.get_converter('unicode_safe'),
                    toolkit.get_converter('convert_from_extras')],
        })
        return schema  
    
    # IValidators
    def get_validators(self):
        return {
            u'owner_org_validator': custom_owner_org_validator,
            u'url_validator': custom_url_validator,
            u'title_validator': custom_title_validator,
            u'location_validator': custom_location_validator
        }
