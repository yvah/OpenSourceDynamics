
      function go()
      {
         var name = document.getElementById('search').value;
          var result = _.find(cities.locations, {'title': name});
          if (!result)
              window.alert('Nothing found');
          else
              window.alert('Go to ' + result.url);
      }