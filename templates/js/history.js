var DropdownButton = ReactBootstrap.DropdownButton;
var MenuItem = ReactBootstrap.MenuItem;

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
    return this.state.podcasts.map(function(podcast) {
      return <Podcast podcast={podcast} />
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
                <PodcastActionDropdown podcast={this.props.podcast} />
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
  render: function() {
    var id = this.props.podcast.id + '-dropdown';
    return (
      <DropdownButton title="Actions" id={id}>
        <MenuItem>Edit...</MenuItem>
        <MenuItem>Delete...</MenuItem>
      </DropdownButton>
    );
  },
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
