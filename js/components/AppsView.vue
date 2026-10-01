<script>
import AppHeader from './AppHeader.vue';
import AppCarousel from './AppCarousel.vue';
import UserInfo from './UserInfo.vue';
import Loader from './Loader.vue';
import Footer from './Footer.vue';

export default {
  components: {
    AppHeader,
    AppCarousel,
    UserInfo,
    Loader,
    Footer
  },
  data() {
    return {
      audio: new Audio(),
      app: null,
      info: 'No Gamepad was Detected. Connect and Press any Button.',
      loader: '',
      currentVersion: 'Fetching version...',
      latestVersion: null,
      updateAvailable: false,
    }
  },
  methods: {
    fetch_version() {
      let self = this;
      axios.get('/version').then((response) => {
        self.currentVersion = response.data.local_version;
        self.latestVersion = response.data.remote_version;
        self.updateAvailable = self.latestVersion.localeCompare(self.currentVersion) > 0;
      }).catch((error) => {
        self.currentVersion = 'Unable to fetch version.'
      });
    },
    refresh() {
      axios.post('/refresh').then((response) => {
        window.location.reload(true);
      }).catch((error) => {
        window.location.reload(true);
      });
    },
    upload() {
      let self = this;
      let dropzone = new Dropzone("div#uploader", { url: "/upload", binaryBody: true})
      dropzone.on("success", function(files, response) {
        self.loader='Waiting for deploy confirmation.';
        let id = response.id;
        let title = response.title + " " + response.subtitle;
        let deploy = confirm("Do you want to deploy the application " + title + "?");
        if (deploy) {
          axios.post('/deploy/' + id).then((response) => {
            self.showMessage('Application installed!',4000, () => self.refresh());
          }).catch((error) => {
            self.showMessage('Failed to deploy application.\nContact application distributer for more information.',4000);
          });
        }
      });
      dropzone.on("error", function(files, response) {
        self.showMessage('Failed to install application.\nContact application distributer for more information.',4000);
      });
      dropzone.hiddenFileInput.click();
      self.loader='Installing application. Please wait...';
    },
    update() {
      let self = this;
      self.loader='Updating system. Please wait...';
      axios.post('/update').then((response) => {
        self.showMessage('Update complete! Reloading system...',4000, () => window.location.reload(true));
      }).catch((error) => {
        self.showMessage('Failed to update system. Try again later.',4000);
      });
    },
    shutdown() {
      this.audio.pause();
      axios.post('/shutdown').then((response) => {
        window.close();
      }).catch((error) => {
        window.close();
      });
      setTimeout(() => {
        window.close();
      }, 500);
    },
    exit() {
      axios.post('/exit').then((response) => {

      }).catch((error) => {
        
      });
    },
    runConfig() {
      this.audio.pause();
      axios.post('/run_config/' + this.app.id).then((response) => {

      }).catch((error) => {
        
      });
    },
    runDefault() {
      this.audio.pause();
      if (this.app.run_sound) {
        this.audio.setAttribute('src',this.app.run_sound);
        this.audio.load();
        this.audio.addEventListener("loadeddata", () => {
          this.audio.play();
        });
        this.audio.addEventListener("canplaythrough", (event) => {
        });
      }
      let self = this;
      axios.post('/run_default/' + this.app.id).then((response) => {
        setTimeout(() => {
          self.loader='Loading application...';
          setTimeout(() => {
            self.loader='';
          },5000)
        },1000)
      }).catch((error) => {
        
      });
    },
    showMessage(text, time, callback) {
      let self = this;
      self.loader=text;
      setTimeout(() => {
        self.loader='';
        if (callback) {
          callback();
        }
      },time);
    },
    onSelect(app) {
      this.app = app;
      console.log(app.title);
      if (this.audio.src != null) {
        // Stop sound?
      };
          console.log("selected: " + app.soundtrack)
      this.audio.setAttribute('src',app.soundtrack);
      this.audio.load();
      this.audio.addEventListener("loadeddata", () => {
        this.audio.play();
      });
      this.audio.addEventListener("canplaythrough", (event) => {
      });
    },
    onRunDefault() {
      this.runDefault();
      
    },
    onDisable() {
      this.audio.pause();
    },
    onAction(action) {
      if (this.loader) {
        return;
      }
      switch(action) {
        case 'refresh':
          this.refresh();
          break;
        case 'upload':
          this.upload();
          break;
        case 'update':
          this.update();
          break;
        case 'settings':
          this.runConfig();
          break;
        case 'shutdown':
          this.shutdown();
          break;
        case 'exit':
          this.exit();
          break;
        default:
      }
    },
    onConnectGamepad() {
      this.info = '';
    },
    onDisconnectGamepad() {
      this.info = 'No Gamepad was Detected. Connect and Press any Button.';
    }
  },
  mounted() {
    window.addEventListener("gamepadconnected", this.onConnectGamepad);
    window.addEventListener("gamepaddisconnected", this.onDisconnectGamepad);
    this.fetch_version();
  },
  unmounted() {
    window.removeEventListener("gamepadconnected", this.onConnectGamepad);
    window.removeEventListener("gamepaddisconnected", this.onDisconnectGamepad);
  }
}
</script>

<template>
  <AppHeader v-bind:updateAvailable="updateAvailable" @onAction="onAction"></AppHeader>
  <AppCarousel @onRunDefault="onRunDefault" @onSelect="onSelect" @onDisable="onDisable"></AppCarousel>
  <UserInfo v-bind:info="info"></UserInfo>
  <Loader v-if="loader" v-bind:info="loader"></Loader>
  <Footer v-bind:currentVersion="currentVersion"></Footer>
  <div style="display: none" id="uploader"></div>
</template>