## LP Podcast

This is a codebase intended to be deployed to an appengine project that allows
for uploading, modifying, and deleting podcast episodes. Some manual configuration
is involved for setting up a new podcast, such as registering it with iTunes and
doing a one-time configuration of an `rss.xml` file.

### How it works
TODO

### Deploying a new podcast appspot

To deploy a new podcast you must:

1. Create a new appengine project
2. Deploy this codebase to that new project
3. Create a new GCS bucket in that appengine project and make it public
4. Add required files to the GCS bucket
3. Configure `EnvVar`s

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
