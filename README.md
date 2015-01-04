Idea Reminder
=============

[ideareminder.org](http://www.ideareminder.org/)

### Set up

1.  Install the [Google App Engine SDK for Python](https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python).
2. Create a `secrets/keys.py` file that defines [your project's API key](https://developers.google.com/api-client-library/python/guide/aaa_apikeys) as `api_key`.
  - On Cloud Console, make sure the "Allowed IPs" field is empty (unless you have static IPs from App Engine). This lets you use the Drive API from your App Engine service account. This is the authentication method your app will use when it's deployed.
3. [Create and configure a Cloud Console service account for local testing](http:/stackoverflow.com/a/22723127/1691482).
  - Unfortunately, the authentication scheme described in #2 doesn't work for local testing, so you'll need a Cloud Console Service Account for local testing. Your command may look something like:

```
dev_appserver.py --log_level debug --appidentity_email_address \
  <some-id>@developer.gserviceaccount.com --appidentity_private_key_path \
  secrets/private_key_for_dev_appserver.pem --clear_datastore=yes ./
```