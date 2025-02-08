import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  // {
  //   path: '/test',
  //   // component: Layout,
  //   component: () => import('@/views/Tables/index'),
  //   meta: { title: 'Home1', icon: 'test' }
  // },
  // {
  //   path: '/Home',
  //   component: Layout,
  //   children: [
  //     {
  //       path: 'index',
  //       name: 'Form',
  //       component: () => import('@/views/form/index'),
  //       meta: { title: 'Home', icon: 'form' }
  //     }
  //   ]
  // },

  // {
  //   path: '/BondPool',
  //   component: Layout,
  //   redirect: '/BondPool',
  //   // meta: { title: 'BondPool', icon: 'form' },
  //   children: [
  //     {
  //       path: 'table',
  //       name: 'BondPoolTable',
  //       component: () => import('@/views/BondPool/index'),
  //       meta: { title: '债券池(demo)', icon: 'table' }
  //     }
  //   ]
  // },
  // {
  //   // path: '/BondSheet',
  //   path: '/',
  //   component: Layout,
  //   redirect: '/BondRate/table',
  //   // meta: { title: 'BondPool', icon: 'form' },
  //   children: [
  //     {
  //       path: 'BondRate/table',
  //       name: 'BondRate',
  //       component: () => import('@/views/BondSheet_rate/index'),
  //       meta: { title: '行情可视化 rate (demo)', icon: 'table' }
  //     }
  //   ]
  // },
  // {
  //   path: '/',
  //   component: Layout,
  //   redirect: '/BondvisNew/table',
  //   // meta: { title: 'BondPool', icon: 'form' },
  //   children: [
  //     {
  //       path: 'BondvisNew/table',
  //       name: 'BondvisNew',
  //       component: () => import('@/views/BondSheet_small/index'),
  //       meta: { title: '行情可视化', icon: 'table' }
  //     }
  //   ]
  // },
  {
    path: '/',
    component: Layout,
    // redirect: '/test/table',
    // meta: { title: 'BondPool', icon: 'form' },
    children: [
      {
        path: 'BondVis/table',
        name: 'test',
        component: () => import('@/views/BondVis/index'),
        meta: { title: 'New design', icon: 'table' }
      }
    ]
  },
  // {
  //   path: '/test',
  //   component: Layout,
  //   // redirect: '/test/table',
  //   // meta: { title: 'BondPool', icon: 'form' },
  //   children: [
  //     {
  //       path: 'test/table',
  //       name: 'test',
  //       component: () => import('@/views/test/index'),
  //       meta: { title: 'New design', icon: 'table' }
  //     }
  //   ]
  // },
  // {
  //   // path: '/BondSheet',
  //   path: '/',
  //   component: Layout,
  //   redirect: '/BondSheet/table',
  //   // meta: { title: 'BondPool', icon: 'form' },
  //   children: [
  //     {
  //       path: 'BondSheet/table',
  //       name: 'BondSheet',
  //       component: () => import('@/views/BondSheet/index'),
  //       meta: { title: '行情可视化 V2(demo)', icon: 'table' }
  //     }
  //   ]
  // },
  // {
  //   // path: '/BondSheet',
  //   path: '/Bondvis2',
  //   component: Layout,
  //   redirect: '/Bondvis2',
  //   // meta: { title: 'BondPool', icon: 'form' },
  //   children: [
  //     {
  //       path: '/Bondvis2',
  //       name: 'Bondvis2',
  //       component: () => import('@/views/Bondvis2/index'),
  //       meta: { title: '行情可视化 V2(demo)', icon: 'table' }
  //     }
  //   ]
  // },
  // {
  //   path: '/Bondvis',
  //   component: Layout,
  //   redirect: '/Bondvis',
  //   children: [{
  //     path: 'Bondvis',
  //     name: 'Bondvis',
  //     component: () => import('@/views/Bondvis/index'),
  //     meta: { title: '行情可视化 V1(demo)', icon: 'dashboard' }
  //   }]
  // },
  // {
  //   path: '/transaction_chain',
  //   component: Layout,
  //   redirect: '/transaction_chain',
  //   children: [{
  //     path: 'Transaction_chain',
  //     name: 'Transaction_chain',
  //     component: () => import('@/views/transaction_chain/index'),
  //     meta: { title: '代持链路(demo)', icon: 'dashboard' }
  //   }]
  // },

  //   children: [
  //     {
  //       path: 'menu1',
  //       component: () => import('@/views/nested/menu1/index'), // Parent router-view
  //       name: 'Menu1',
  //       meta: { title: 'Menu1' },
  //       children: [
  //         {
  //           path: 'menu1-1',
  //           component: () => import('@/views/nested/menu1/menu1-1'),
  //           name: 'Menu1-1',
  //           meta: { title: 'Menu1-1' }
  //         },
  //         {
  //           path: 'menu1-2',
  //           component: () => import('@/views/nested/menu1/menu1-2'),
  //           name: 'Menu1-2',
  //           meta: { title: 'Menu1-2' },
  //           children: [
  //             {
  //               path: 'menu1-2-1',
  //               component: () => import('@/views/nested/menu1/menu1-2/menu1-2-1'),
  //               name: 'Menu1-2-1',
  //               meta: { title: 'Menu1-2-1' }
  //             },
  //             {
  //               path: 'menu1-2-2',
  //               component: () => import('@/views/nested/menu1/menu1-2/menu1-2-2'),
  //               name: 'Menu1-2-2',
  //               meta: { title: 'Menu1-2-2' }
  //             }
  //           ]
  //         },
  //         {
  //           path: 'menu1-3',
  //           component: () => import('@/views/nested/menu1/menu1-3'),
  //           name: 'Menu1-3',
  //           meta: { title: 'Menu1-3' }
  //         }
  //       ]
  //     },
  //     {
  //       path: 'menu2',
  //       component: () => import('@/views/nested/menu2/index'),
  //       name: 'Menu2',
  //       meta: { title: 'menu2' }
  //     }
  //   ]
  // },
  // {
  //   path: 'external-link',
  //   component: Layout,
  //   children: [
  //     {
  //       path: 'https://panjiachen.github.io/vue-element-admin-site/#/',
  //       meta: { title: 'External Link', icon: 'link' }
  //     }
  //   ]
  // },
  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
