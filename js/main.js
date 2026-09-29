const { loadModule } = window['vue3-sfc-loader'];

document.body.style.cursor = 'none';

const options = {
    moduleCache: {
        'vue': Vue,
        'vue3-carousel': VueCarousel,
    },
    async getFile(url) {
        const res = await fetch(url);
        if ( !res.ok )
            throw Object.assign(new Error(res.statusText + ' ' + url), { res });
        return {
            getContentData: asBinary => asBinary ? res.arrayBuffer() : res.text(),
        }
    },
    addStyle(textContent) {
        const style = Object.assign(document.createElement('style'), { textContent });
        const ref = document.head.getElementsByTagName('style')[0] || null;
        document.head.insertBefore(style, ref);
    },
}

loadModule('./components/AppsView.vue', options).then( (component) => {
    const app = Vue.createApp(component)
    app.mount('#app')
})

document.body.addEventListener('click', () => {
    document.body.style.cursor = 'auto';
}, true); 
