#! .env/bin/python
# *-* coding: utf-8 *-*

import random
import time
import requests
from celery.signals import task_postrun
from celery.utils.log import get_task_logger
from leadgen import celery, db
from leadgen.models import Message, Lead
from sqlalchemy import exc

logger = get_task_logger(__name__)

domains = ['outlook.com', 'gmail.com', 'icloud.com', 'hotmail.com', 'yahoo.com', 'us.army.mil', 'mail.com',
           'zohomail.com', 'gmx.com', 'hushmail.com', 'fastmail.com', 'inbox.com', 'space.com', 'gmx.com',
           'protonmail.com', 'mail.yandex.com', 'webmail.com', 'cfl.rr.com', 'mybrighthouse.com', 'tampabay.rr.com',
           'msn.com', 'live.com', 'web.de', 'verizon.com', 'att.net', 't-mobile.com', 'sprint.com', 'embarq.com',
           'comcast.net', 'dish.com', 'bell.com', 'dell.com', 'sc.rr.com', 'prodigy.net', 'centurylink.com', 'juno.com',
           'ibm.com', 'spectrum.com', 'mindspring.com', 'compuserve.com', 'earthlink.net', 'mpinet.net', 'digex.com',
           'xfinity.com', 'clearwire.com', 'netzero.net']


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@celery.task
def log(message):
    """Print some log messages"""
    logger.debug(message)
    logger.info(message)
    logger.warning(message)
    logger.error(message)
    logger.critical(message)


@celery.task
def reverse_messages():
    """Reverse all messages in DB"""

    try:
        messages = db.session.query(Message).one()

        for message in messages:

            words = message.text.split()

            for word in words:
                message_text = " ".join(reversed(word))

                message = Message(
                    text=message_text
                )

                # add and commit
                db.session.add(message)
                db.session.commit()
                logger.info('Wrote {} to the database...'.format(message_text))

    except exc.SQLAlchemyError as db_err:
        # log the result
        logger.warning('Database returned error: {}'.format(db_err))


@celery.task(max_retries=3)
def create_lead():
    """
    Create the new lead from the call to Random User
    :param id:
    :return: db response
    """
    hdr = {'user-agent': 'Mozilla/Linux 5.0', 'content-type': 'application/json'}
    nat = 'us,gb,fr,de'
    num_results = 1000
    base_url = 'https://randomuser.me/api?nat=' + nat + '&results=' + str(num_results)

    try:
        r = requests.get(base_url, headers=hdr)

        if r.status_code == 200:
            results = r.json()['results']
            info = r.json()['info']

            # loop our results
            for result in results:

                # create the new lead obj
                lead = Lead(
                    gender=result['gender'].title(),
                    name_title=result['name']['title'].title(),
                    name_first=result['name']['first'].title(),
                    name_last=result['name']['last'].title(),
                    location_street=result['location']['street'].title(),
                    location_city=result['location']['city'].title(),
                    location_state=result['location']['state'].title(),
                    location_postcode=result['location']['postcode'],
                    email=result['email'],
                    email_verified=0,
                    login_username=result['login']['username'],
                    login_password=result['login']['password'],
                    login_salt=result['login']['salt'],
                    login_md5=result['login']['md5'],
                    login_sha1=result['login']['sha1'],
                    login_sha256=result['login']['sha256'],
                    date_of_birth=result['dob'],
                    date_registered=result['registered'],
                    cell_phone=result['cell'],
                    home_phone=result['phone'],
                    nationality=result['nat'],
                    nat_id_type=result['id']['name'],
                    nat_id_value=result['id']['value'],
                    img_lg=result['picture']['large'],
                    img_md=result['picture']['medium'],
                    img_thumb=result['picture']['thumbnail'],
                    seed=info['seed']
                )

                # add and commit the new lead obj
                db.session.add(lead)
                db.session.commit()
                logger.info('New lead added: {} {} {} - ({})'.format(
                    lead.name_title, lead.name_first, lead.name_last, lead.gender
                ))

        elif r.status_code == 404:
            logger.warning('The API call returned a 404 error.  Task aborted...')
        elif r.status_code == 503:
            logger.warning('The API call returned a 503 error.  Task aborted...')
        elif r.status_code == 502:
            logger.warning('The API call returned a 502 error.  Task aborted...')
        else:
            logger.warning('The API call returned a {} error.  Task aborted...'.format(r.status_code))

    except requests.HTTPError as err:
        logger.info('The API call returned error: {}'.format(str(err)))


@celery.task(max_retries=3)
def update_lead_email(id):
    """
    Update and verify the lead email address
    :param id:
    :return: resp
    """
    if not isinstance(id, int):
        id = int(id)

    try:
        lead = db.session.query(Lead).filter(
            Lead.id == id,
            Lead.email_verified == 0
        ).one()

        if lead:

            # get the current email address and split off example.com
            email = lead.email.split('@')
            new_email = email[0] + '@' + random.choice(domains)

            try:
                # set the email address to verified
                lead.email = new_email
                lead.email_verified = True
                db.session.commit()

                # log the result
                logger.info('Lead ID: {} email address was updated and verified: {}'.format(id, new_email))

            except exc.SQLAlchemyError as err:
                # log the result
                logger.critical('Database returned error: {}'.format(str(err)))

        return id

    except exc.SQLAlchemyError as err:
        # log the result
        logger.critical('Database returned error: {}'.format(str(err)))


@celery.task
def verify_emails():
    """
    Get a queryset from the database and verify the email addresses
    :param id:
    :return: async result
    """

    lead_count = 0

    try:
        leads = db.session.query(Lead).filter(
            Lead.email_verified == 0
        ).limit(100).all()

        if leads:

            for lead in leads:
                # call the async task
                update_lead_email.delay(lead.id)
                lead_count += 1

            # log the result
            logger.info('Lead Generator airdropped {} leads into '
                        'the Email Address Verification Queue'.format(str(lead_count)))

        else:
            # log the result
            logger.info('The query did not find any lead emails addresses to verify.  Task aborted!')

        return lead_count

    except exc.SQLAlchemyError as err:
        # log the result
        logger.info('Database returned error: {}'.format(str(err)))


@celery.task(max_retries=3)
def geocode_address(id):
    """
    Geocode Address from Google Maps API
    :param id:
    :return: json
    """
    if not isinstance(id, int):
        id = int(id)

    # task vars
    address = None
    country = None
    county = None
    state = None
    locality = None
    api_key = 'your-api-key-here'
    hdr = {'user-agent': 'Mozilla/Linux 5.0', 'content-type': 'application/json'}

    # get our lead by task param 'id'
    try:
        lead = db.session.query(Lead).filter(
            Lead.id == id
        ).one()

        if lead:
            address = '{}+,{},+{}+{}'.format(lead.location_street, lead.location_city, lead.location_state,
                                             lead.location_postcode)

            url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(address, api_key)

            # call geocode api
            try:
                r = requests.get(url, headers=hdr)

                # did google maps geocoding api respond to our request?
                if r.status_code == 200:

                    # set var to json obj
                    results = r.json()['results']

                    # loop our result set
                    for result in results:
                        location_type = result['geometry']['location_type']
                        latitude = result['geometry']['location']['lat']
                        longitude = result['geometry']['location']['lng']
                        place_id = result['place_id']

                        for x in result['address_components']:
                            if x['types'][0] == 'locality':
                                locality = x['long_name']
                            elif x['types'][0] == 'administrative_area_level_2':
                                county = x['long_name']
                            elif x['types'][0] == 'administrative_area_level_1':
                                state = x['long_name']
                            elif x['types'][0] == 'country':
                                country = x['long_name']

                        # set lead vars from address components
                        lead.location_type = location_type
                        lead.location_latitude = latitude
                        lead.location_longitude = longitude
                        lead.location_county = county
                        lead.location_country = country
                        lead.location_place_id = place_id

                        # commit to the database
                        db.session.commit()

                        # log the result
                        logger.info('Lead ID: {} - {} {} from {}, {} '
                                    'was successfully geocoded @ LAT: {} LONG: {} '
                                    'PLACE ID: {} by the API.'.format(id, lead.name_first, lead.name_last, locality,
                                                                      state, latitude, longitude, place_id))

                else:
                    # log the result
                    logger.warning('The Google Maps API returned a {} error.  Task aborted.'.format(str(r.status_code)))

            except requests.HTTPError as http_err:
                # log the result
                logger.warning('The Google Maps API could not be reached for geocoding.  Task aborted.')

        # return the lead 'id'
        return id

    except exc.SQLAlchemyError as err:
        # log the result
        logger.critical('Database returned error: {}'.format(str(err)))


@celery.task
def generate_addresses_for_geocode():
    """
    Return a list of Leads to Geocode physical address
    :return: int(count)
    """
    lead_count = 0

    try:
        leads = db.session.query(Lead).filter(
            Lead.location_geocoded == 0
        ).limit(100).all()

        if leads:

            # loop the leads list
            # and call the task
            for lead in leads:

                # air drop to geocode
                geocode_address.delay(lead.id)
                lead_count += 1

            # log the result
            logger.info('Lead Generator airdropped {} leads into the geocode '
                        'task queue to send to Google Maps API'.format(lead_count))

        else:
            # log the result
            logger.warning('Lead Generator count not find any Lead addresses to geocode.  Task aborted.')

        return lead_count

    except exc.SQLAlchemyError as err:
        # log the result
        logger.critical('Database returned error: {}'.format(str(err)))


@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()


def reversed(words):
    """
    Reverse the words in a string
    :param words:
    :return: reversed string
    """
    return words[::-1]
