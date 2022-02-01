<template>
  <v-app id="app">
    <div
      :id="userTakeScreenshot ? 'screenshot' : ''"
      class="container"
      @mousemove="move"
      @mousedown="mouseDown"
      @mouseup="mouseUp"
    >
      <p style="position:absolute">Utilize o mouse para selecionar a área desejada</p>
      
      <transition name="screenshot" v-if="userTakeScreenshot">
        <div class="Flash" v-if="tookScreenShot"></div>
      </transition>
      <div
        :class="{ highlighting: mouseIsDown, overlay: userTakeScreenshot }"
        :style="{ borderWidth: borderWidth }"
      >
      </div>
      
      <div
        class="borderedBox"
        :class="{ hidden: !isDragging }"
        :style="{
          left: boxLeft + 'px',
          top: boxTop + 'px',
          width: boxEndWidth + 'px',
          height: boxEndHeight + 'px',
        }"
      ></div>
      <span
        ref="tooltip"
        class="tooltip"
        :class="{ hidden: !isDragging }"
        :style="{ left: toolTipLeft + 'px', top: toolTipTop + 'px' }"
        >{{ boxEndWidth }} x {{ boxEndHeight }}px</span
      >

      <v-navigation-drawer
        app
        clipped
        v-model="drawer"
        mini-variant-width="70"
        :mini-variant.sync="mini"
        :permanent="permanent"
        :expand-on-hover="!permanent"
        width="300"
      >
        <v-list :shaped="!mini" :rounded="mini && !permanent && drawer">
          <v-list-item
            v-for="item in items"
            :key="item.title"
            link
            color="purple darken-2"
            :class="`${
              $vuetify.theme.dark ? 'grey--text text--lighten-2' : ''
            } ${!mini ? 'pl-6' : ''}`"
            :to="item.to"
          >
            <v-list-item-icon>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content class="text-left">
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
        <template v-slot:append>
          <v-divider />
          <div class="px-0 mx-0">
            <v-list>
              <v-list-item
                link
                :class="`${
                  $vuetify.theme.dark ? 'grey--text text--lighten-2' : ''
                } ${!mini ? 'pl-6' : ''}`"
              >
                <v-list-item-icon>
                  <v-icon v-text="'mdi-message-alert-outline'" />
                </v-list-item-icon>
                <v-list-item-content class="text-left">
                  <v-list-item-title> Enviar feedback</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </div>
        </template>
      </v-navigation-drawer>
      <v-app-bar
        app
        clipped-left
        elevation="0"
        class="px-2"
        dark
        :color="!$vuetify.theme.dark ? 'purple darken-4' : ''"
      >
        <v-app-bar-nav-icon @click="checkTheAction()" />
        <v-toolbar-title :color="$vuetify.theme.dark ? 'purple darken-4' : ''"
          >Title</v-toolbar-title
        >
      </v-app-bar>
      <v-main>
        <v-switch v-model="userTakeScreenshot" inset />

        <div class="img-container mt-12 mx-12" style="border: 6px solid orange">
          <img :src="imageUrl" class="screenshot-img" id="screenshotImg" />
        </div>
        <v-container fluid>
          <router-view />
        </v-container>
      </v-main>
    </div>
  </v-app>
</template>
<script>
import html2canvas from "html2canvas";
var tooltip;

export default {
  data() {
    return {
      drawer: true,
      items: [
        { title: "Home", icon: "mdi-home-city", to: "/" },
        { title: "My Account", icon: "mdi-account" },
        { title: "Users", icon: "mdi-account-group-outline" },
      ],
      mini: false,
      permanent: true,
      mouseIsDown: false,
      isDragging: false,
      tookScreenShot: false, // After the mouse is released

      // Used to calculate where to start showing the dragging area
      startX: 0,
      startY: 0,
      endX: 0,
      endY: 0,

      crosshairs: null,
      overlay: null,

      borderWidth: "",

      // Handling the positioning of the crosshairs
      crossHairsLeft: 0,
      crossHairsTop: 0,

      // The box that contains the border and all required numbers.
      boxTop: 0,
      boxLeft: 0,
      boxEndWidth: 0,
      boxEndHeight: 0,

      // The tooltip's required positioning numbers.
      toolTipLeft: 0,
      toolTipTop: 0,
      toolTipWidth: 0,
      toolTipHeight: 0,

      windowHeight: 0,
      windowWidth: 0,
      TOOLTIP_MARGIN: null,
      isMouseDown: false,
      imageUrl: null,
      userTakeScreenshot: false,
    };
  },
  watch: {
    TOOLTIP_MARGIN() {
      if (this.userTakeScreenshot) {
        this.TOOLTIP_MARGIN = window
          .getComputedStyle(document.querySelector(".tooltip"))
          .margin.split("px")[0];
      }
    },
  },
  beforeMount() {
    if (!this.$vuetify.breakpoint.xl) {
      this.permanent = false;
    }
  },
  mounted() {
    tooltip = this.$refs.tooltip;
    /* console.log(tooltip);
    tooltip = document.querySelector(".tooltip"); */
    this.windowWidth =
      window.innerWidth ||
      document.documentElement.clientWidth ||
      document.body.clientWidth;
    this.windowHeight =
      window.innerHeight ||
      document.documentElement.clientHeight ||
      document.body.clientHeight;
    this.toolTipWidth = tooltip.getBoundingClientRect().width;
    // To recalculate the width and height if the screen size changes.
    window.onresize = function () {
      this.windowWidth =
        window.innerWidth ||
        document.documentElement.clientWidth ||
        document.body.clientWidth;
      this.windowHeight =
        window.innerHeight ||
        document.documentElement.clientHeight ||
        document.body.clientHeight;
    };
  },
  methods: {
    checkTheAction() {
      if (this.$vuetify.breakpoint.xl) {
        this.mini = !this.mini;
        this.permanent = this.mini ? false : true;
      } else {
        this.openSidebar();
      }
    },
    openSidebar() {
      this.permanent = false;
      this.drawer = !this.drawer;
      this.mini = false;
    },
    getSelectRect() {
      if (this.userTakeScreenshot) {
        const [left, top] = [
          Math.min(this.startX, this.endX),
          Math.min(this.startY, this.endY),
        ];
        const [right, bottom] = [
          Math.max(this.startX, this.endX),
          Math.max(this.startY, this.endY),
        ];
        const [width, height] = [right - left, bottom - top];
        return { left, top, right, bottom, width, height };
      }
    },
    drawShadow() {
      if (this.userTakeScreenshot) {
        const verticalScrollBarWidth = 16;
        const rc = this.getSelectRect();
        this.boxTop = rc.top;
        this.boxLeft = rc.left;
        this.boxEndWidth = rc.width;
        this.boxEndHeight = rc.height;
        this.borderWidth =
          rc.top +
          "px " +
          (this.windowWidth - rc.right - verticalScrollBarWidth) +
          "px " +
          (this.windowHeight - rc.bottom) +
          "px " +
          rc.left +
          "px";
      }
    },
    placeTooltip({ startX, startY, endX, endY }) {
      if (this.userTakeScreenshot) {
        if (endX >= startX && endY >= startY) {
          this.toolTipLeft =
            endX + this.toolTipWidth >= this.windowWidth
              ? this.windowWidth - this.toolTipWidth - this.TOOLTIP_MARGIN * 2
              : endX;
          this.toolTipTop =
            endY + this.toolTipHeight + this.TOOLTIP_MARGIN * 2 >=
            this.windowHeight
              ? this.windowHeight - this.toolTipHeight - this.TOOLTIP_MARGIN * 2
              : endY;
        } else if (endX <= startX && endY >= startY) {
          this.toolTipLeft =
            endX - this.toolTipWidth <= 0
              ? this.TOOLTIP_MARGIN
              : endX - this.toolTipWidth;
          this.toolTipTop =
            endY + this.toolTipHeight + this.TOOLTIP_MARGIN * 2 >=
            this.windowHeight
              ? this.windowHeight - this.toolTipHeight - this.TOOLTIP_MARGIN * 2
              : endY;
        } else if (endX >= startX && endY <= startY) {
          this.toolTipLeft =
            endX + this.toolTipWidth >= this.windowWidth
              ? this.windowWidth - this.toolTipWidth - this.TOOLTIP_MARGIN * 2
              : endX;
          this.toolTipTop =
            endY - this.toolTipHeight <= 0
              ? this.TOOLTIP_MARGIN
              : endY - this.toolTipHeight;
        } else if (endX <= startX && endY <= startY) {
          this.toolTipLeft =
            endX - this.toolTipWidth <= 0
              ? this.TOOLTIP_MARGIN
              : endX - this.toolTipWidth;
          this.toolTipTop =
            endY - this.toolTipHeight <= 0
              ? this.TOOLTIP_MARGIN
              : endY - this.toolTipHeight;
        }
      }
    },
    move(e) {
      if (this.userTakeScreenshot) {
        this.crossHairsTop = e.clientY;
        this.crossHairsLeft = e.clientX;
        var tooltipBoundingRect = tooltip.getBoundingClientRect();
        this.toolTipWidth = tooltipBoundingRect.width;
        this.toolTipHeight = tooltipBoundingRect.height;
        this.isDragging = this.mouseIsDown;
        if (this.isDragging) {
          const endY = (this.endY = e.clientY);
          const endX = (this.endX = e.clientX);
          const startX = this.startX;
          const startY = this.startY;
          this.placeTooltip({ startX, startY, endX, endY });
          this.drawShadow();
        }
      }
    },
    mouseDown(e) {
      if (this.userTakeScreenshot) {
        this.borderWidth = this.windowWidth + "px " + this.windowHeight + "px";
        this.startX = e.clientX;
        this.startY = e.clientY;
        this.toolTipWidth = tooltip.getBoundingClientRect().width;
        this.mouseIsDown = true;
        this.tookScreenShot = false;
      }
    },
    mouseUp(e) {
      if (this.userTakeScreenshot) {
        if (this.isDragging) {
          this.endX = e.clientX;
          this.endY = e.clientY;
          this.isDragging = false;
          this.mouseIsDown = false;
          this.takeScreenshot();
          this.tookScreenShot = true;
        }
      }
    },
    takeScreenshot() {
      if (this.userTakeScreenshot) {
        const rc = this.getSelectRect();
        html2canvas(document.querySelector("body")).then((canvas) => {
          const croppedCanvas = document.createElement("canvas");
          croppedCanvas.width = rc.width;
          croppedCanvas.height = rc.height;
          const croppedCanvasContext = croppedCanvas.getContext("2d");
          croppedCanvasContext.drawImage(
            canvas,
            rc.left,
            rc.top,
            rc.width,
            rc.height,
            0,
            0,
            rc.width,
            rc.height
          );
          this.imageUrl = croppedCanvas.toDataURL();
          const screenshotImg = document.getElementById("screenshotImg");
          screenshotImg.src = this.imageUrl;
        });
      }
    },
  },
};
</script>
<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

/* Foundation */
*,
*:before,
*:after {
  box-sizing: border-box;
}

html,
body {
  padding: 0;
  margin: 0;
  height: 100%;
}

.overlay,
.crosshairs,
.tooltip,
.borderedBox {
  user-select: none;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 100;
}

.overlay.highlighting {
  background: none;
  border-color: rgba(0, 0, 0, 0.5);
  border-style: solid;
}

/* .crosshairs {
  height: 100%;
  position: absolute;
  width: 100%;
  z-index: 2147483645;
}

.crosshairs.hidden {
  display: none;
}

.crosshairs::before,
.crosshairs::after {
  content: "";
  height: 100%;
  width: 100%;
  position: absolute;
  border: none !important;
  border-image: 0 !important;
}

.crosshairs::before {
  left: -100%;
  top: -100%;
  border-right: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3) !important;
}

.crosshairs::after {
  left: 0px;
  top: 0px;
  border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-left: 1px solid rgba(255, 255, 255, 0.3) !important;
} */

.container {
  clear: both;
  overflow: hidden;
  width: 100%;
  height: 100%;
  background-repeat: no-repeat;
  background-size: cover;
}

.borderedBox {
  border: 1px solid #fff;
  position: absolute;
}

.borderedBox.hidden {
  display: none;
}

.tooltip {
  display: inline-block;
  position: absolute;

  background-color: grey;
  color: #fff;

  border-radius: 4px;

  font-size: 12px;
  font-family: monospace;

  padding: 6px;
  margin: 6px;
  white-space: nowrap;
  z-index: 100;
}

.tooltip.hidden {
  display: none;
}

.Flash {
  position: absolute;
  width: 100%;
  height: 100%;

  top: 0;
  left: 0;

  background-color: #fff;
  z-index: 2147483646;

  opacity: 1;

  animation-delay: 0.2s;
  animation-name: fade-out;
  animation-duration: 1s;
  animation-iteration-count: 1;
  animation-fill-mode: forwards;
}

.screenshot-enter-active,
.screenshot-leave-active {
  transition: opacity 0.2s;
}

.screenshot-enter, .screenshot-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}

@keyframes fade-out {
  from {
    opacity: 1;
  }

  to {
    opacity: 0;
  }
}
</style>
