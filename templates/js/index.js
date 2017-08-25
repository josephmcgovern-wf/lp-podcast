var HomePage = React.createClass({
    render: function() {
      return (
        <div className="jumbotron">
          <div className="container">
            <h1>Let's add a podcast</h1>
            <a href="/upload/">
              <button className="btn btn-primary btn-lg">Get Started</button>
            </a>
          </div>
        </div>
      )
    }
});

var page = document.getElementById('page');
ReactDOM.render(
    <HomePage />, page
);
