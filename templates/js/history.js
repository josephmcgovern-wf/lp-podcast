var DropdownButton = ReactBootstrap.DropdownButton;
var MenuItem = ReactBootstrap.MenuItem;
var Modal = ReactBootstrap.Modal;

var HistoryPage = React.createClass({
  getInitialState: function() {
    return {
      podcastsReceived: false,
      podcasts: [],
      isLoading: false,
    };
  },
  componentWillMount: function() {
    this.syncPodcasts();
  },
  render: function() {
    return (
      <div>
        <div>
        </div>
        <div className="page-header">
          <h2>Podcast History</h2>
        </div>
        <div className="col-md-8 col-md-offset-2">
          {this.getContent()}
        </div>
      </div>
    )
  },
  getContent: function() {
    if (this.state.isLoading) {
      return <Jumbotron message="Loading podcasts..."/>
    }
    else if (this.state.podcastsReceived && this.state.podcasts.length == 0) {
      return <NoPodcastsDiv />
    }
    return this.getPodcasts();
  },
  getPodcasts: function() {
    var _this = this;
    return this.state.podcasts.map(function(podcast) {
      return <Podcast podcast={podcast} onUpdate={_this.syncPodcasts}
                      onDelete={_this.syncPodcasts}/>
    });
  },
  syncPodcasts: function() {
    var _this = this;
    _this.setState({isLoading: true});
    $.ajax({
      url: '/api/internal/podcast/',
      method: 'GET',
      success: function(json) {
        var data = JSON.parse(json);
        _this.setState({podcasts: data.podcasts});
      },
      error: function(data) {
        // TODO display error
      },
      complete: function() {
        _this.setState({isLoading: false, podcastsReceived: true});
      }
    });
  },
});

var Podcast = React.createClass({
  render: function() {
    return (
      <div className="panel panel-default">
        <div className="panel-heading">
          <div className="row">
            <div className="col-md-6">
              <h4>
                <div>
                  {this.props.podcast.name}
                </div>
                <div>
                  <small>{this.props.podcast.subtitle}</small>
                </div>
              </h4>
            </div>
            <div className="col-md-6">
              <div className="pull-right">
                <PodcastActionDropdown podcast={this.props.podcast}
                                       onDelete={this.props.onDelete}
                                       onUpdate={this.props.onUpdate}/>
              </div>
            </div>
          </div>
        </div>
        <div className="panel-body">
          <div>
            {this.props.podcast.description}
          </div>
        </div>
      </div>
    );
  }
});

var PodcastActionDropdown = React.createClass({
  getInitialState: function() {
    return {
      showEditModal: false,
      showDeleteModal: false
    }
  },
  render: function() {
    var id = this.props.podcast.id + '-dropdown';
    return (
      <DropdownButton title="Manage" id={id}>
        <MenuItem onClick={this.openEditModal}>Edit...</MenuItem>
        <MenuItem onClick={this.openDeleteModal}>Delete...</MenuItem>
        <EditModal show={this.state.showEditModal}
                   onClose={() => this.setState({showEditModal: false})}
                   podcast={this.props.podcast}
                   onUpdate={this.props.onUpdate}/>
        <DeleteModal show={this.state.showDeleteModal}
                     onClose={() => this.setState({showDeleteModal: false})}
                     podcast={this.props.podcast}
                     onDelete={this.props.onDelete}/>
      </DropdownButton>
    );
  },
  openEditModal: function() {
    this.setState({showEditModal: true});
  },
  openDeleteModal: function() {
    this.setState({showDeleteModal: true});
  },
});

var EditModal = React.createClass({
  getInitialState: function() {
    return {
      name: this.props.podcast.name,
      description: this.props.podcast.description,
      subtitle: this.props.podcast.subtitle,
      dateRecorded: this.props.podcast.date_recorded,
      isLoading: false
    };
  },
  render: function() {
    return (
      <Modal show={this.props.show} onHide={this.close}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Podcast Episode</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {this.getFormContent()}
        </Modal.Body>
        <Modal.Footer>
          <button className="btn btn-default" onClick={this.close}
                  disabled={this.state.isLoading}>Cancel</button>
          <button className="btn btn-primary" onClick={this.submit}
                  disabled={this.state.isLoading}>
            {this.state.isLoading? "Submitting..." : "Submit"}</button>
        </Modal.Footer>
      </Modal>
    );
  },
  getFormContent: function() {
    return (
      <div>
        <div className="form-group">
          <label>Episode Name <small className="help-text">(Sermon Title)</small></label>
          <input type="text" className="form-control" placeholder="Name"
                 value={this.state.name}
                 onChange={(e) => this.setState({name: e.target.value})}/>
        </div>
        <div className="form-group">
          <label>Description</label>
          <textarea className="form-control" placeholder="A long description of the episode"
                    value={this.state.description}
                    style={ {resize: 'y'} }
                    onChange={(e) => this.setState({'description': e.target.value})}/>
        </div>
        <div className="form-group">
          <label>Subtitle <small className="help-text">(Sermon Series)</small></label>
          <input type="text" className="form-control" placeholder="A subtitle for this episode"
                 value={this.state.subtitle}
                 onChange={(e) => this.setState({'subtitle': e.target.value})}/>
        </div>
        <div className="form-group" >
          <label>Date Episode Recorded <small className="help-text">(Date of Sermon)</small></label>
          <div className="input-group">
            <Datetime value={this.state.dateRecorded}
                      onChange={(newDate) => this.setState({dateRecorded: newDate})}
                      dateFormat='YYYY-MM-DD'
                      timeFormat={false}/>
            <span className="input-group-addon btn btn-default">
              <span className="glyphicon glyphicon-calendar" />
            </span>
          </div>
        </div>
      </div>
    );
  },
  close: function() {
    this.props.onClose();
  },
  submit: function() {
    var _this = this;
    this.setState({isLoading: true});
    // TODO Populate data
    var data = {};
    $.ajax({
      url: '/api/internal/podcast/' + _this.props.podcast.id + '/',
      method: 'PUT',
      data: JSON.stringify({podcast_data: data}),
      contentType: 'application/json',
      success: function() {
        console.log('success');
        _this.props.onUpdate();
        _this.close();
      },
      error: function() {
        // TODO Display error
        console.log('error');
      },
      complete: function() {
        _this.setState({isLoading: false});
      }
    });
  }
});

var DeleteModal = React.createClass({
  getInitialState: function() {
    return {
      isLoading: false
    }
  },
  render: function() {
    return (
      <Modal show={this.props.show} onHide={this.close}>
        <Modal.Header closeButton>
          <Modal.Title>Delete Podcast Episode</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Are you sure you want to delete this podcast episode? <strong>This action cannot be undone.</strong>
          </p>
        </Modal.Body>
        <Modal.Footer>
          <button className="btn btn-default" onClick={this.close}
                  disabled={this.state.isLoading}>Cancel</button>
          <button className="btn btn-danger" onClick={this.deletePodcast}
                  disabled={this.state.isLoading}>
            {this.state.isLoading ? "Deleting..." : "Delete"}</button>
        </Modal.Footer>
      </Modal>
    );
  },
  close: function() {
    this.props.onClose();
  },
  deletePodcast: function() {
    var _this = this;
    this.setState({isLoading: true});
    $.ajax({
      url: '/api/internal/podcast/' + _this.props.podcast.id + '/',
      method: 'DELETE',
      success: function() {
        console.log('success');
        _this.props.onDelete();
        _this.close();
      },
      error: function() {
        // TODO Display error
        console.log('error');
      },
      complete: function() {
        _this.setState({isLoading: false});
      }
    });
  }
});

var Jumbotron = React.createClass({
  render: function() {
    return (
      <div className="jumbotron">
        <div className="container">
          <span style={ {textAlign: 'center'} }>
            <h3>{this.props.message}</h3>
            {this.props.children}
          </span>
        </div>
      </div>
    )
  },
});

var NoPodcastsDiv = React.createClass({
  render: function() {
    return (
      <Jumbotron message="Uh oh! No podcasts exist" children={this.getChildren()} />
    );
  },
  getChildren: function() {
    return (
      <span className="col-md-offset-5">
        <a href='/upload/'>
          <button className="btn btn-primary btn-lg">
            Add a podcast
          </button>
        </a>
      </span>
    )
  },
});

var page = document.getElementById('page');
ReactDOM.render(
    <HistoryPage  />, page
);
