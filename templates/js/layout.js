var NAME_TO_PATH_MAP = {
  'Upload': '/upload/',
  'History': '/history/'
};

var Navbar = React.createClass({
  getDefaultProps: function() {
    return {
      currentPagePath: '/'
    };
  },
  render: function() {
    return (
      <nav className="navbar navbar-default navbar-fixed-top">
        <div className="container-fluid">
          {this.getBrand()}
          {this.getNavigationItems()}
        </div>
      </nav>
    );
  },
  getBrand: function() {
    var href = this.props.currentPagePath == "/" ? "#" : "/";
    return (
      <div className="navbar-header">
        <a className="navbar-brand" href={href}>Home</a>
      </div>
    );
  },
  getNavigationItems: function() {
    return (
      <div className="collapse navbar-collapse">
        <ul className="nav navbar-nav">
          {this.getItems()}
        </ul>
      </div>
    );
  },
  getItems: function() {
    var items = [];
    for (var name in NAME_TO_PATH_MAP) {
      var className = "";
      var path = NAME_TO_PATH_MAP[name]
      if (this.props.currentPagePath == path) {
        className = "active";
        path = "#";
      }
      items.push(
        <li className={className}><a href={path}>{name}</a></li>
      );
    }
    return items;
  },
});


var navDom = document.getElementById('page-nav');
ReactDOM.render(
  <Navbar currentPagePath={window.location.pathname} />, navDom);
