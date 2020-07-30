var Alert = ReactBootstrap.Alert;
var ProgressBar = ReactBootstrap.ProgressBar;

var audio = new Audio();
var DURATION = null;
audio.addEventListener("canplaythrough", function() {
  DURATION = audio.duration;
})

var UploadPage = React.createClass({
  getInitialState: function() {
    return {
      alertContent: '',
      alertClass: 'danger'
    }
  },
  render: function() {
    return (
      <div>
        <div style={ {position: 'fixed', zIndex: '100', top: '60px', left: '35%'} }
             ref="alertContainer">
          {this.getAlert()}
        </div>
        <div className="page-header" style={ {marginTop: '4em'} }>
          <h1>Add Podcast Episode</h1>
        </div>
        <div>
          <p className="text-muted">Please fill out the information below</p>
        </div>
        <div>
          <UploadForm updateAlert={this.updateAlert}/>
        </div>
      </div>
    )
  },
  getAlert: function() {
    if (!this.state.alertContent) {
      return;
    }
    return (
      <Alert bsStyle={this.state.alertClass} onDismiss={this.handleAlertDismissed}>
        {this.state.alertContent}
      </Alert>
    );
  },
  updateAlert: function(alertContent, alertClass) {
    this.setState({
      alertContent: alertContent,
      alertClass: alertClass
    });
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
        date_recorded: moment(),
      },
      progress: 0
    };
  },
  render: function() {
    return (
      <div>
        <div className="row">
          <div className="col-md-5">
            <PodcastForm data={this.state.formData}
                         onUpdate={this.updateData}
                         onSubmit={this.submit}
                         isUploading={this.state.isUploading}
                         onAudioFileChange={this.updateAudioFile}
                         ref="podcastForm"/>
          </div>
        </div>
        <div className="row">
          <div className="col-md-12" style={ {marginTop: '1.5em'} }>
            {this.getProgressBar()}
          </div>
        </div>
      </div>
    )
  },
  getProgressBar: function() {
    if (!this.state.isUploading) {
      return null;
    }
    return (
      <ProgressBar now={this.state.progress} />
    );
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
    var missingFields = this.getMissingFields();
    if (missingFields) {
      this.failValidation(missingFields);
      return;
    }
    this.setState({isUploading: true});
    this.uploadAudioFile(this.sendPodcastRequest);
  },
  failValidation: function(missingFields) {
    var content = (
      <span>
        <strong>Hold your horses!</strong> The following fields must be filled out:
        <p>{missingFields}</p>
      </span>
    );
    this.props.updateAlert(content, 'danger');
  },
  getMissingFields: function() {
    var invalidAttrs = [];
    for (var key in this.state.formData) {
      if (!this.state.formData[key]) {
        invalidAttrs.push(key);
      }
    }
    if (!this.state.audioFile) {
      invalidAttrs.push('audio file');
    }
    if (invalidAttrs.length > 0) {
      return invalidAttrs.join(', ');
    }
    return null;
  },
  uploadAudioFile: function(callback) {
    var _this = this;
    var el = document.getElementById('audio-form');
    var form_data = new FormData(el);
    form_data.append('audioFile', this.state.audioFile);
    var file = this.state.audioFile;
    var _this = this;
    $.getJSON(
      '/api/internal/podcast/generate_upload_url/', {
        filename: encodeURIComponent(file.name),
        content_type: file.type
      }, function(json) {
        $.ajax({
          url: json.url,
          method: 'PUT',
          data: form_data,
          contentType: file.type,
          processData: false,
          cache: false,
          crossDomain: true,
          xhr: function() {
            var myXhr = $.ajaxSettings.xhr();
            if(myXhr.upload){
              myXhr.upload.addEventListener('progress', _this.updateProgressFromFileUpload, false);
            }
            return myXhr;
          },
          success: function() {
            _this.setState({progress: 90});
            if (callback) {
              callback();
            }
          },
          error: function(data) {
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
            _this.props.updateAlert(content, 'danger');
            _this.setState({isUploading: false});
          },
        });
      }
    );
  },
  updateProgressFromFileUpload: function(e) {
    if (e.lengthComputable) {
      var max = e.total;
      var current = e.loaded;
      var percentage = (current * 100)/max;
      this.setState({progress: percentage * 0.8});
    }
  },
  sendPodcastRequest: function() {
    var _this = this;
    var data = this.state.formData;
    data.audio_file_length = this.state.audioFile.size;
    data.duration = DURATION;
    data.date_recorded = data.date_recorded.format('YYYY-MM-DD');
    data.audio_filename = this.state.audioFile.name;
    $.ajax({
      url: '/api/internal/podcast/',
      method: 'POST',
      data: JSON.stringify(data),
      contentType: 'application/json',
      success: function(data) {
        _this.setState({progress: 100});
        var content = (
          <span>
            <p>
              <b>Good news!</b> This podcast episode has been successfully uploaded
            </p>
            <p>
              The new episode should appear in iTunes within 48 hours
            </p>
          </span>
        );
        _this.props.updateAlert(content, 'success');
      },
      error: function(data) {
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
        _this.props.updateAlert(content, 'danger');
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
        {this.getDatepicker()}
        {this.getAudioFormGroup()}
        {this.getSubmitButton()}
      </form>
    );
  },
  getNameFormGroup: function() {
    return (
      <div className="form-group">
        <label>Episode Name <small className="help-text">(Sermon Title)</small></label>
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
        <label>Subtitle <small className="help-text">(Sermon Series)</small></label>
        <input type="text" className="form-control" placeholder="A subtitle for this episode"
               value={this.props.data.subtitle}
               onChange={(e) => this.props.onUpdate('subtitle', e.target.value)}/>
      </div>
    );
  },
  getDatepicker: function() {
    return (
      <div className="form-group" >
        <label>Date Episode Recorded <small className="help-text">(Date of Sermon)</small></label>
        <div className="input-group">
          <Datetime value={this.props.data.date_recorded}
                    onChange={this.updateDate}
                    dateFormat='YYYY-MM-DD'
                    timeFormat={false}/>
          <span className="input-group-addon btn btn-default">
            <span className="glyphicon glyphicon-calendar" />
          </span>
        </div>
      </div>
    );
  },
  updateDate: function(newDate) {
    this.props.onUpdate('date_recorded', newDate);
  },
  getAudioFormGroup: function() {
    return (
      <div className="form-group">
        <label>Audio file</label>
        <form id="audio-form" enctype="mutlipart/form-data" method="POST">
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
