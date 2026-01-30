<script setup>
import axios from 'axios'

let dev = import.meta.env.MODE === 'development'
dev = false
let base_url = dev ? 'http://192.168.2.220:7861' : 'https://jokkad-danmu-search.hf.space'

base_url = dev ? 'http://127.0.0.1:5173' : 'https://github.xiaodu1234.xyz'

let HLSModule = null
let DPlayerModule = null
onMounted(async () => {
  init_player('', null)
})
// let ok = ref(null)
let links = ref([])
let selectedIndex = ref(-1)
let selectedIndex1 = ref(-1)
let av_selected = ref(-1)
const isActive = ref(true)
const isKVM = ref(true)
const isAV = ref(false)
let av_links = ref([])
let search_btn = ref(null)
let playerdiv = ref(null)
let dialogVisible = ref(false)

let dp = null
let ok = ref('')

const init_player = (my_url, danmus) => {
  // --- 2. 初始化 DPlayer ---
  dp = new window.DPlayer({
    container: document.getElementById('dplayer'),
    autoplay: false,
    chromecast: true,
    screenshot: false,
    video: {
      url: my_url,
      type: my_url.endsWith('.m3u8') ? 'hls' : 'auto',

    },
    danmaku: {
      speedRate: 1,
    },
  })
}

const search = async () => {
  const search = ok.value
  const cache = isActive.value
  if (!search || search.trim().length < 1) {
    ElMessage.error('请输入搜索内容')
    return
  }
  if (dp) {
    dp.pause()
  }
  const Loading = ElLoading.service({
    lock: true,
    // text: 'Loading',
    // svg: true,
    // spinner: 'el-icon-loading',
    background: 'rgba(0, 0, 0, 0.3)',
  })
  console.log(Loading)
  selectedIndex.value = -1
  selectedIndex1.value = -1
  let res = null
  try {
    res = await axios.get(`${base_url}/search`, {
      params: {
        q: search,
        cache: cache,
        isKVM: isKVM.value,
        isAV: isAV.value,
      },
      timeout: isKVM.value ? 66000 : 30000,
    })
  } catch (e) {
    console.log(e)
    ElMessage.error('搜索失败, 请稍后重试')
    Loading.close()
    return
  }

  Loading.close()

  let isok = false
  if (isAV.value) {
    links.value = []
    let datas = res.data['message']
    if (datas.length > 0) {
      av_links.value = datas
      isok = true
      av_selected.value = -1
    }
  } else {
    av_selected.value = -1
    let datas = res.data['message']
    console.log(datas)

    if (datas.length > 0) {
      av_links.value = []
      links.value = datas
      isok = true
      itemClick(0, 0)
    }
  }
  if (isok) {
    ElMessage.success('搜索成功')
  } else {
    ElMessage.error('未找到结果, 请稍后重试')
  }
}

const itemClick = async (index1, index) => {
  const item = links.value[index1][index]
  // alert(item)
  console.log(links.value[index1][index])
  console.log(1)
  selectedIndex.value = index
  selectedIndex1.value = index1
  const search = ok.value
  // const Loading = ElLoading.service({
  //   background: 'rgba(0, 0, 0, 0.3)'
  // })

  if (!search || search.trim().length < 1) {
    ElMessage.error('请输入搜索内容')
    return
  }
  console.log(2)
  if (dp) {
    console.log('switch')
    dp.switchVideo(
      {
        url: item,

        type: item.endsWith('.m3u8') ? 'hls' : 'auto',
      },
      {
        addition: [
          `${base_url}/danmu?q=${search}&page=${index}&size=${links.value[index1].length}`,
        ],
      },
    )
    dp.play()
  }

  // Loading.close()
}

const reload = async () => {
  dialogVisible.value = true
}

const confirm = async () => {
  dialogVisible.value = false

  try {
    await axios.get(`${base_url}/trigger`)
  } finally {
    ElMessage.success('正在重启服务器')
  }
}

const avItemClick = (av, index) => {
  console.log(av[4])
  av_selected.value = index
  let url = av[4]
  if (url.length === 0 || !url.startsWith('http')) {
    ElMessage.error('链接未找到')
    return
  }
  // todo : 恶心啊
  const proxiedUrl = `/proxy-m3u8?url=${encodeURIComponent(url)}`
  dp.switchVideo({
    url: url,
    type: url.endsWith('.m3u8') ? 'hls' : 'auto',
  })
  const currentScrollTop =
    window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop
  console.log(currentScrollTop)
  console.log(search_btn.value.$el)
  const btn_bottom = search_btn.value.$el.getBoundingClientRect().bottom
  window.scrollTo({
    top: btn_bottom + currentScrollTop,
    behavior: 'smooth',
  })

  setTimeout(() => {
    dp.play()
  }, 800)
}
</script>

<template>
  <div class="container">
    <div class="hbox">
      <h1>弹幕播放器</h1>
      <!--      <button id="commit">确认</button>-->

      <el-switch v-model="isKVM" />
      <h5>KVM源(视频高清)</h5>
      <el-switch v-model="isAV" />
      <h5>种子</h5>
      <div class="cache_btn">
        <ElButton id="commit" @click="reload">重启服务器</ElButton>
        <el-switch v-model="isActive" />
        <h5>缓存开关</h5>
      </div>
    </div>

    <div class="search_box">
      <el-input
        placeholder="输入精确的视频名字"
        v-model="ok"
        clearable
        @keydown.enter.prevent="search"
      />

      <ElButton id="commit" @click="search" ref="search_btn">搜索</ElButton>
    </div>
    <!--    <input type="text" id="url" placeholder="输入精确的视频名字" ref="ok"/>-->
    <div id="dplayer" ref="playerdiv"></div>
    <div id="line" v-for="(item1, index1) in links" :key="item1.id">
      <h5>线路{{ index1 }}</h5>
      <div
        v-for="(item, index) in item1"
        :key="item.id"
        @click="itemClick(index1, index)"
        :class="{ select: index === selectedIndex && index1 === selectedIndex1 }"
      >
        {{ index + 1 }}
      </div>
    </div>

    <div id="av" v-if="av_links.length > 0">
      <div
        class="box"
        @click="avItemClick(av, index)"
        v-for="(av, index) in av_links"
        :key="av.id"
        :class="av_selected === index ? 'av_select' : ''"
      >
        <img v-lazy="`/proxy-img?url=${encodeURIComponent(av[3])}`" alt="" :key="av[3]" />
        <span class="title">{{ av[0] }}</span>
        <div class="look_box">
          <span>播放 {{ av[1] }}</span>
          <span>点赞 {{ av[2] }}</span>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="确定重启服务器" width="300">
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" :style="{ width: '60px' }">取消</el-button>
          <el-button type="primary" @click="confirm" :style="{ width: '60px' }"> 确定 </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
@import './index.less';
</style>
