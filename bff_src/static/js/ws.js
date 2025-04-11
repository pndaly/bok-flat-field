

const CLIENT_ID = Date.now()
const WS_RETRY = 1000 // millaseconds, how long to wait to reconnect
const WS_PAGE = `/ws/${CLIENT_ID}`; // Must match URL
const HEARTBEAT = { "heartbeat": "pong" }; // Must return over websocket

// Globals
var ws;
var setCallbacks = {};

document.addEventListener("DOMContentLoaded", () => {
  wsStart();
})

const wsStart = () => {
  // Creates websocket connection
  if ("WebSocket" in window) {
    var loc = window.location;
    var url = `ws:${loc.host}${WS_PAGE}`
    console.log(url);
    ws = new WebSocket(url);

    // indicate lost connection
    ws.onclose = (event) => {
      if (event.wasClean) {
        console.warn(`Web Socket connection closed cleanly, code=${event.code}`);
      }
      else {
        console.warn(`Web Socket connection died, code=${event.code}`);
      }
      // restart web socket
      ws = null;
      setTimeout(() => {wsStart()}, WS_RETRY);
    };

    ws.onerror = (event) => {
      console.error(`Web Socket error`)
    };

    // dispatch incoming messages
    ws.onmessage = (event) => {
      var json = JSON.parse(event.data);

      if (json.heartbeat) {
        ws.send(JSON.stringify(HEARTBEAT));
        return;
      }

      // Update the properties
      updateProperties(json);
    };

    ws.onopen = (event) => {
      console.log('Websocket is open');
    }

  }
  else {
    alert("Web Socket is not supported by this Browser");
  }
}

const setPropertyCallback = (property, callback) => {
  console.debug(`Setting callback for property: ${property}`)
  setCallbacks[property] = callback;

  return;
}

const updateProperties = (data) => {
  var property = Object.keys(data)[0];
  var callback = setCallbacks[property] || setCallbacks["*"];

  if (callback) {
    callback(data);
  }

  return;
}
