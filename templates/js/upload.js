var Alert = ReactBootstrap.Alert;

var audio = new Audio();
var DURATION = null;
audio.addEventListener("canplaythrough", function() {
  DURATION = audio.duration;
})

var UploadPage = React.createClass({
    getInitialState: function() {
      return {
        alertContent: ''
      }
    },
    render: function() {
      return (
        <div>
          {this.getAlert()}
          <div className="page-header">
            <h1>Add Podcast Episode</h1>
          </div>
          <div>
            <p className="text-muted">Please fill out the information below</p>
          </div>
          <div className="row">
            <UploadForm onError={this.updateAlert}/>
          </div>
        </div>
      )
    },
  getAlert: function() {
    if (!this.state.alertContent) {
      return;
    }
    return (
      <Alert bsStyle='danger' onDismiss={this.handleAlertDismissed}>
        {this.state.alertContent}
      </Alert>
    );
  },
  updateAlert: function(alertContent) {
    this.setState({alertContent: alertContent});
  },
  handleAlertDismissed: function() {
    this.setState({alertContent: ''});
  },
});

var UploadForm = React.createClass({
  getInitialState: function() {
    return {
      isUploading: false,
      audioFile: null,
      formData: {
        name: null,
        description: null,
        subtitle: null,
        keywords: [],
      }
    };
  },
  render: function() {
    this.props.podcastForm = (
      <PodcastForm data={this.state.formData}
                       onUpdate={this.updateData}
                       onSubmit={this.submit}
                       isUploading={this.state.isUploading}
                       onAudioFileChange={this.updateAudioFile}
                       ref="podcastForm"/>
    );
    return (
      <div>
        <div className="col-md-5">
          {this.props.podcastForm}
        </div>
        <div className="col-md-4 col-md-offset-1" style={ {display: 'none'} }>
          <div className="text-center">
            <img className="img-responsive" src="http://www.planwallpaper.com/static/images/abstract-colourful-cool-wallpapers-55ec7905a6a4f.jpg" />
            <button className="btn btn-primary btn-lg" style={ {marginTop: '1em'} }>
              Upload Episode Image
            </button>
            <div className="checkbox">
                <label>
                  <input type="checkbox" /> Use the same image as last time
                </label>
            </div>
          </div>
        </div>
      </div>
    )
  },
  updateData: function(formName, formValue) {
    var formData = this.state.formData;
    formData[formName] = formValue;
    this.setState({formData: formData});
  },
  updateAudioFile: function(file) {
    this.setState({audioFile: file});
  },
  submit: function() {
    this.setState({isUploading: true});
    this.sendAudioFileRequest(
      this.sendPodcastRequest);
  },
  sendAudioFileRequest: function(callback) {
    var _this = this;
    var el = document.getElementById('audio-form');
    var data = new FormData(el);
    data.append('audioFile', this.state.audioFile);
    $.ajax({
      url: '{{upload_url}}',
      method: 'POST',
      data: data,
      processData: false,
      contentType: false,
      cache: false,
      success: function(jsonifiedData) {
        var data = JSON.parse(jsonifiedData);
        var audioUrl = data.url
        console.log("Audio url", audioUrl);
        if (callback) {
          callback(audioUrl);
        }
      },
      error: function(data) {
        console.log("Big error");
        var content = (
          <span>
            <p>
              <b>Uh-oh!</b> There was a problem creating this podcast.
              Please see the error below:
            </p>
            <p>
              {data.responseText}
            </p>
          </span>
        );
        _this.props.onError(content);
        _this.setState({isUploading: false});
      },
    });
  },
  sendPodcastRequest: function(audioUrl) {
    var _this = this;
    var data = this.state.formData;
    var file = document.getElementById('file-upload');
    data.audio_file_length = this.state.audioFile.size;
    data.audio_file_url = audioUrl;
    data.duration = DURATION;
    $.ajax({
      url: '/api/internal/podcast/',
      method: 'POST',
      data: JSON.stringify(data),
      contentType: 'application/json',
      success: function(data) {
        console.log('Success!');
      },
      error: function(data) {
        console.log("Small Error");
        var content = (
          <span>
            <p>
              <b>Uh-oh!</b> There was a problem creating this podcast.
              Please see the error below:
            </p>
            <p>
              {data.responseText}
            </p>
          </span>
        );
        _this.props.onError(content);
      },
      complete: function() {
        _this.setState({isUploading: false});
      }
    });

  },
  getDurationString: function() {
    var seconds = Math.round(DURATION % 60);
    var totalMinutes = Math.floor(DURATION / 60);
    var minutes = totalMinutes % 60;
    var hours = totalMinutes / 60;
    var hoursStr = hours.toString();
    if (hours < 10) {
      hoursStr = '0' + hoursStr;
    }
    var minuteStr = minutes.toString();
    if (minutes < 10) {
      minuteStr = '0' + minuteStr;
    }
    var secondsStr = seconds.toString();
    if (seconds < 10) {
      secondsStr = '0' + secondsStr;
    }
    return hoursStr + ":" + minuteStr + ":" + secondsStr;
  },
});

var PodcastForm = React.createClass({
  componentWillUpdate: function(nextProps, nextState) {
    if (nextState != this.state) {
      this.props.onUpdate(nextState);
    }
  },
  render: function() {
    return (
      <form ref="form">
        {this.getNameFormGroup()}
        {this.getDescriptionFormGroup()}
        {this.getSubtitleFormGroup()}
        {this.getKeywordsFormGroup()}
        {this.getAudioFormGroup()}
        {this.getSubmitButton()}
      </form>
    );
  },
  getNameFormGroup: function() {
    return (
      <div className="form-group">
        <label>Episode Name</label>
        <input type="text" className="form-control" placeholder="Name"
               value={this.props.data.name}
               onChange={(e) => this.props.onUpdate('name', e.target.value)}/>
      </div>
    );
  },
  getDescriptionFormGroup: function() {
    return (
      <div className="form-group">
        <label>Description</label>
        <textarea className="form-control" placeholder="A long description of the episode"
                  value={this.props.data.description}
                  onChange={(e) => this.props.onUpdate('description', e.target.value)}/>
      </div>
    );
  },
  getSubtitleFormGroup: function() {
    return (
      <div className="form-group">
        <label>Subtitle</label>
        <input type="text" className="form-control" placeholder="A subtitle for this episode"
               value={this.props.data.subtitle}
               onChange={(e) => this.props.onUpdate('subtitle', e.target.value)}/>
      </div>
    );
  },
  getKeywordsFormGroup: function() {
    return (
      <div className="form-group">
        <label>Keywords</label>
        <Select.Creatable className="select-createable"
                          options={[]}
                          multi={true}
                          onChange={this.handleKeywordChange}
                          value={this.getKeywordsForCreatable()}
                          placeholder={"Add keywords..."}
                          noResultsText='' />
      </div>
    );
  },
  handleKeywordChange: function(newKeywords) {
    var keywords = newKeywords.map(function(keyword) {
      return keyword.value;
    });
    this.props.onUpdate('keywords', keywords);
  },
  getKeywordsForCreatable: function() {
    return this.props.data.keywords.map(function(keyword) {
      return {label: keyword, value: keyword};
    });
  },
  getAudioFormGroup: function() {
    return (
      <div className="form-group">
        <label>Audio file</label>
        <form id="audio-form" enctype="mutlipart/form-data" action="{{upload_url}}"
              method="POST">
         <input id='file-upload' type="file" accept="audio/*"
                onChange={this.handleAudioFileChange}
                ref={'fileUpload'} />
        </form>
      </div>
    );
  },
  handleAudioFileChange: function() {
    var file = this.refs.fileUpload.files[0];
    var objectUrl = URL.createObjectURL(file);
    audio.src = objectUrl;
    this.props.onAudioFileChange(file);
  },
  getSubmitButton: function() {
    var text = this.props.isUploading ? 'Submitting...' : 'Submit';
    return (
      <button type="button" className="btn btn-primary"
              onClick={this.props.onSubmit} disabled={this.props.isUploading}>
        {text}
      </button>
    );

  }
});

var page = document.getElementById('page');
ReactDOM.render(
    <UploadPage  />, page
);
