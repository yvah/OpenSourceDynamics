//Create a Cognos Dashboard Embedded Session
var createSession = function(){

   const createSessionUrl = "/session";

   var clientId = document.getElementById('client-id-input').value;
   var clientSecret = document.getElementById('client-secret-input').value;
   var webDomain = window.location.href;

   fetch(createSessionUrl, {
       method : "POST",
       body: JSON.stringify({clientId: clientId, clientSecret: clientSecret, webDomain: webDomain})
   }).then(
       response => response.json() // .json(), etc.
       // same as function(response) {return response.text();}
   ).then(
      function(resp){
         console.log(resp);

      //   var sessionCodeSpan = document.getElementById("session-code-span");
      //   sessionCodeSpan.innerHTML = resp.sessionCode;
      //   sessionCodeSpan.dataset.sessionCode = resp.sessionCode;

      //   //Persist client ID for use later
      //   var clientIdDataSpan = document.getElementById("client-id-data-span");
      //   clientIdDataSpan.dataset.clientId = clientId;
      
      // loadDashboards(clientId);

      var api = new CognosApi({cognosRootURL: 'https://eu-gb.dynamic-dashboard-embedded.cloud.ibm.com/daas/',
         node: document.getElementById('cognos'),
         sessionCode: resp.sessionCode,
         language: 'en'
      })
      api.initialize()
      const dashboardApi = null;
      api.dashboard.openDashboard({
         dashboardSpec: {...} // preset dashboard, with preloaded data
      }).then((dashboardAPI) => {
         console.log('Dashboard opened successfully.');
         dashboardApi = dashboardAPI;
      });

      }
   );
};
