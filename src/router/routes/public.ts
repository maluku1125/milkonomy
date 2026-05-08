import type { RouteRecordRaw } from "vue-router"
import locale from "@/locales"

const Layouts = () => import("@/layouts/index.vue")
const { t } = locale.global

/**
 * 公开路由配置（個人版精簡）
 * 僅保留 Dashboard / Enhancer / Enhanposer 三個頁面
 */
export const publicRoutes: RouteRecordRaw[] = [
  {
    path: "/redirect",
    component: Layouts,
    meta: {
      hidden: true
    },
    children: [
      {
        path: ":path(.*)",
        component: () => import("@/pages/redirect/index.vue")
      }
    ]
  },
  {
    path: "/403",
    component: () => import("@/pages/error/403.vue"),
    meta: {
      hidden: true
    }
  },
  {
    path: "/404",
    component: () => import("@/pages/error/404.vue"),
    meta: {
      hidden: true
    },
    alias: "/:pathMatch(.*)*"
  },
  {
    path: "/",
    component: Layouts,
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        component: () => import("@/pages/dashboard/index.vue"),
        name: "Dashboard",
        meta: {
          title: t("首页"),
          svgIcon: "dashboard",
          affix: true
        }
      }
    ]
  },
  {
    path: "/",
    component: Layouts,
    redirect: "/enhancer",
    children: [
      {
        path: "enhancer",
        component: () => import("@/pages/enhancer/index.vue"),
        name: "Enhancer",
        meta: {
          title: t("强化计算"),
          elIcon: "MagicStick",
          affix: true
        }
      }
    ]
  },
  {
    path: "/",
    component: Layouts,
    redirect: "/enhanposer",
    children: [
      {
        path: "enhanposer",
        component: () => import("@/pages/enhanposer/index.vue"),
        name: "Enhanposer",
        meta: {
          title: t("强化分解"),
          affix: false,
          svgIcon: "dashboard"
        }
      }
    ]
  },
  {
    path: "/link",
    meta: {
      title: t("相关链接"),
      elIcon: "Link"
    },
    children: [
      {
        path: "https://www.milkywayidle.com/",
        component: () => {},
        name: "LinkMWI",
        meta: {
          title: "Milky Way Idle"
        }
      },
      {
        path: "https://milkywayidle.wiki.gg/",
        component: () => {},
        name: "LinkWiki",
        meta: {
          title: "MWI Wiki"
        }
      }
    ]
  }
]
