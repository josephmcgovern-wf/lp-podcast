## LP Podcast

This is a codebase intended to be deployed to an appengine project that allows
for uploading, modifying, and deleting podcast episodes. Some manual configuration
is involved for setting up a new podcast, such as registering it with iTunes and
doing a one-time configuration of an `rss.xml` file.

There is a [sample rss file](./sample_rss.xml) that can be used to get a new
podcast started. New episodes are added as `<item>` elements in the rss file, 
nested within the `<channel>` tag.

### How it works

This app runs an on-demand instance whenever someone accesses the application.
It is a simple web UI for uploading some basic metadata about an episode (
name, description, date, etc) along with the audio file necessary. The audio
file gets uploaded to a folder in the podcast bucket and the rss feed xml file
gets updated with the episode content, pointing to the new audio file.

### Future improvements

* Add unit tests
* More thoughtfully consider the wsgi server & its configuration
* Support other podcast apps (right now only iTunes is supported)
* Write a tiny script to assist in spinning up new podcasts
    * Friendly script for building out rss.xml
    * This could be expanded to creating the project, assigning permissions, 
    creating bucket, etc.

### Deploying a new podcast appspot

To deploy a new podcast you must:

1. Create a new appengine project
2. Deploy this codebase to that new project
3. Create a new GCS bucket in that appengine project and make it public
4. Add required files to the GCS bucket
5. Configure `EnvVar`s
6. Enable the `IAM Service Account Credentials API` and give the default service 
account the `Service Account Token Creator` role.
7. Configure third party podcast apps to see this new feed.

#### Files in the bucket

The bucket should look like the following:
```
audio/
images/logo.png
rss/rss.xml
```

Audio files will be uploaded to the audio directory.
The logo.png file will be be shown as the podcast logo (this is referenced in `rss.xml`)
The `rss.xml` file is what iTunes reads to make gather podcast information.

#### Required EnvVars:

The following environment variables must be put into the datastore before the
application can be used properly:

`whitelisted_emails`
`bucket_name`
`FLASK_SECRET_KEY` (generate from a [random password generator](https://passwordsgenerator.net/))
`GOOGLE_CLIENT_ID`
`GOOGLE_CLIENT_SECRET`

The google client id and secret must be generated as an oauth web app client credential.
This can be generated from the IAM page of the new project.
