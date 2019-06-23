const client = AgoraRTC.createClient({ mode: "live", codec: "h264" });

let init = false;

function streamInit() {
  client.init(
    "f2dfe4fd76b042a4adc81a87d1d2511c",
    () => {
      console.log("AgoraRTC client initialized");
      client.join(null, "publishing", null, uid => {
        console.log(`User ${uid} joined`);
        AgoraRTC.getDevices(devices => {
          let audioId = null;
          devices.forEach(item => {
            if (item.kind === "audioinput") {
              audioId = item.deviceId;
            }
          });

          const localStream = AgoraRTC.createStream({
            streamID: uid,
            audio: false,
            video: true,
            screen: false
          });

          localStream.init(
            () => {
              console.log("Stream initialised");
              let canvas = document.querySelector("#canvas");
              let stream = canvas.captureStream(25).getVideoTracks()[0];
              localStream.replaceTrack(
                stream,
                () => {
                  console.log("Success stream replaced");
                  client.publish(localStream, err => {
                    console.error(`Publish local stream error: ${err}`);
                  });
                },
                err => console.error(`Error: ${err}`)
              );
            },
            err => {
              console.error(`Error created: ${err}`);
            }
          );
        });
      });
    },
    err => {
      console.log("AgoraRTC client init failed", err);
    }
  );
}

// setInterval(() => {
//   $.ajax({
//     url: "fetch_recent_audio",
//     success: (res, stat) => {
//       if (!res["status"]) {
//         let audio = document.getElementById('audio');
//         console.log(res["audio_path"])
//         audio.setAttribute('src', res['audio_path']);
//         audio.load();
//         if(!init){
//           streamInit();
//           init = true;
//         }
//         audio.play();
//       }
//     },
//     error: (xhr, status) => {
//       console.log(xhr);
//     }
//   })
// }, 3000);

streamInit();
