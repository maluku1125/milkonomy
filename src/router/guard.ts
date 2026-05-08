import type { Router } from "vue-router"
import { setRouteChange } from "@@/composables/useRouteListener"
import { useTitle } from "@@/composables/useTitle"
import { isInFreezePeriod, isRouteAllowed } from "@@/config/freeze"
import NProgress from "nprogress"
import { usePermissionStoreOutside } from "@/pinia/stores/permission"

NProgress.configure({ showSpinner: false })
const { setTitle } = useTitle()

export function registerNavigationGuard(router: Router) {
  // 全局前置守卫
  router.beforeEach(async (to, _from) => {
    NProgress.start()
    usePermissionStoreOutside().setRoutes([])

    // 检查冻结期间的路由访问权限（個人版冻结已停用，仍保留判断邏輯以防未來使用）
    if (isInFreezePeriod()) {
      const routeName = to.name as string
      if (!isRouteAllowed(routeName)) {
        NProgress.done()
        return { name: "Dashboard" }
      }
    }
  })

  // 全局后置钩子
  router.afterEach((to) => {
    setRouteChange(to)
    setTitle(to.meta.title)
    NProgress.done()
  })
}