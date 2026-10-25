<template>
  <FullScreenLayout>
    <div class="min-h-screen w-full flex flex-col lg:flex-row bg-white dark:bg-gray-900">
      <!-- LEFT PANE: Sign In Form -->
      <div
        class="w-full lg:w-1/2 min-h-screen flex flex-col justify-between p-6 sm:p-10 lg:p-12 xl:p-14 bg-white dark:bg-gray-900 overflow-y-auto"
      >
        <!-- Top branding header -->
        <div class="flex items-center justify-between w-full max-w-md mx-auto">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-500/10 border border-brand-200 dark:border-brand-500/20 text-brand-700 dark:text-brand-300 text-xs font-semibold">
            <span class="w-2 h-2 rounded-full bg-brand-500 animate-pulse"></span>
            CloudScale Technologies
          </div>
          <span class="text-xs text-gray-400 font-medium">Customer Portal</span>
        </div>

        <!-- Center Form Box -->
        <div class="w-full max-w-md mx-auto my-auto py-6">
          <div class="mb-6">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
              Customer Sign In
            </h1>
            <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1.5 leading-relaxed">
              Enter your customer credentials to access your autonomous VM rightsizing console.
            </p>
          </div>

          <!-- Credentials Form -->
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div>
              <label for="email" class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Customer Email<span class="text-error-500">*</span>
              </label>
              <input
                v-model="email"
                type="email"
                id="email"
                required
                placeholder="user@company.com"
                class="w-full h-11 px-3.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-transparent text-sm text-gray-900 dark:text-white placeholder:text-gray-400 focus:border-brand-500 focus:ring-3 focus:ring-brand-500/15 focus:outline-hidden dark:bg-gray-900 transition-all shadow-xs"
              />
            </div>

            <div>
              <div class="flex items-center justify-between mb-1">
                <label for="password" class="block text-xs font-semibold text-gray-700 dark:text-gray-300">
                  Password<span class="text-error-500">*</span>
                </label>
              </div>
              <div class="relative">
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  required
                  placeholder="••••••••••••"
                  class="w-full h-11 pl-3.5 pr-10 rounded-xl border border-gray-300 dark:border-gray-700 bg-transparent text-sm text-gray-900 dark:text-white placeholder:text-gray-400 focus:border-brand-500 focus:ring-3 focus:ring-brand-500/15 focus:outline-hidden dark:bg-gray-900 transition-all shadow-xs"
                />
                <button
                  type="button"
                  @click="togglePasswordVisibility"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  <svg class="w-4 h-4 fill-current" viewBox="0 0 20 20">
                    <path v-if="!showPassword" fill-rule="evenodd" clip-rule="evenodd" d="M10 13.86C7.23 13.86 4.87 12.14 3.92 9.7 4.87 7.27 7.23 5.54 10 5.54s5.13 1.73 6.08 4.16c-.95 2.44-3.31 4.16-6.08 4.16zm0-9.82C6.48 4.04 3.49 6.31 2.42 9.46c-.06.16-.06.33 0 .49 1.07 3.15 4.06 5.41 7.58 5.41s6.51-2.26 7.58-5.41c.06-.16.06-.33 0-.49C16.51 6.31 13.52 4.04 10 4.04zm0 3.8a1.86 1.86 0 1 0 0 3.72 1.86 1.86 0 0 0 0-3.72z" />
                    <path v-else fill-rule="evenodd" clip-rule="evenodd" d="M4.64 3.58a.75.75 0 0 0-1.06 1.06l1.27 1.27C3.75 6.84 2.89 8.06 2.42 9.46a.75.75 0 0 0 0 .49c1.07 3.15 4.06 5.41 7.58 5.41 1.25 0 2.44-.29 3.5-.81l1.86 1.87a.75.75 0 1 0 1.06-1.06L4.64 3.58zm7.72 9.84-1.91-1.91c-.14.03-.29.05-.45.05a1.86 1.86 0 0 1-1.86-1.86c0-.15.02-.3.05-.44L5.92 6.98C5.04 7.69 4.34 8.63 3.92 9.7c.95 2.44 3.31 4.16 6.08 4.16.83 0 1.63-.16 2.36-.44zm3.72-3.72c-.29.75-.72 1.44-1.26 2.03l1.06 1.06c.75-.81 1.34-1.78 1.7-2.85a.75.75 0 0 0 0-.49c-1.07-3.15-4.06-5.41-7.58-5.41-.87 0-1.7.14-2.48.39l1.23 1.23c.4-.08.82-.12 1.25-.12 2.77 0 5.13 1.73 6.08 4.16z" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="isSubmitting"
              class="w-full h-11 flex items-center justify-center rounded-xl bg-brand-500 hover:bg-brand-600 active:scale-[0.99] text-white text-sm font-bold shadow-md shadow-brand-500/20 transition-all cursor-pointer disabled:opacity-50 mt-2"
            >
              <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ isSubmitting ? 'Authenticating...' : 'Sign In to Resource Console' }}</span>
            </button>
          </form>

          <!-- Super Admin Quick Fill Badge -->
          <div class="mt-4 p-3 rounded-xl bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800/40 text-xs">
            <div class="flex items-center justify-between">
              <div class="font-semibold text-purple-900 dark:text-purple-300 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-purple-500"></span>
                Super Admin Account
              </div>
              <button
                type="button"
                @click="fillSuperAdmin"
                class="text-[11px] font-bold text-purple-700 dark:text-purple-300 hover:underline cursor-pointer"
              >
                Quick Fill
              </button>
            </div>
            <p class="text-[11px] text-purple-700/80 dark:text-purple-300/80 mt-1 font-mono">
              admin@smartcloud.com • Admin@123
            </p>
          </div>

          <div class="mt-4 text-center">
            <span class="text-xs text-gray-500">Don't have an account? </span>
            <router-link to="/signup" class="text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline">
              Create an account with Supabase
            </router-link>
          </div>
        </div>

        <!-- Footer -->
        <div class="w-full max-w-md mx-auto pt-4 text-center text-[11px] text-gray-400 dark:text-gray-500">
          SmartCloud Optimizer FinOps Engine v2.1.0 • Supabase Auth
        </div>
      </div>

      <!-- RIGHT PANE: Brand Hero Panel (Sticky & 100% Height - Zero Gaps) -->
      <div
        class="hidden lg:flex lg:w-1/2 min-h-screen sticky top-0 h-screen bg-brand-950 dark:bg-black/50 text-white flex-col justify-center items-center p-8 xl:p-14 overflow-hidden border-l border-brand-900/60 relative"
      >
        <common-grid-shape />
        <div class="absolute -top-24 -right-24 w-96 h-96 bg-brand-500/20 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-brand-600/15 rounded-full blur-3xl pointer-events-none"></div>

        <div class="relative z-10 flex flex-col items-center max-w-md text-center">
          <div class="w-18 h-18 rounded-3xl bg-brand-500/20 border border-brand-400/30 backdrop-blur-md flex items-center justify-center mb-6 shadow-2xl text-brand-300">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
              <line x1="6" y1="6" x2="6.01" y2="6"></line>
              <line x1="6" y1="18" x2="6.01" y2="18"></line>
            </svg>
          </div>

          <h2 class="text-3xl font-extrabold text-white tracking-tight mb-3">
            SmartCloud Optimizer
          </h2>

          <p class="text-sm text-gray-300 leading-relaxed mb-8">
            Autonomous VM Rightsizing, Dynamic Auto-scaling Permissions, and Docker Model Container Telemetry.
          </p>

          <!-- 3 Capability Badges -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
            <div class="p-3.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
              <div class="flex items-center gap-2 text-xs font-bold text-brand-300 mb-1">
                <span class="w-2 h-2 rounded-full bg-brand-400"></span>
                Off-Hours Scaling
              </div>
              <p class="text-[11px] text-gray-400">
                Automatic downscaling during low-usage windows (7 PM – 5 AM).
              </p>
            </div>

            <div class="p-3.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs">
              <div class="flex items-center gap-2 text-xs font-bold text-brand-300 mb-1">
                <span class="w-2 h-2 rounded-full bg-brand-400"></span>
                Bottleneck Radar
              </div>
              <p class="text-[11px] text-gray-400">
                Proactive capacity upgrades before &gt;85% saturation causes outages.
              </p>
            </div>

            <div class="p-3.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xs sm:col-span-2">
              <div class="flex items-center gap-2 text-xs font-bold text-brand-300 mb-1">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                Docker Model VM Integration
              </div>
              <p class="text-[11px] text-gray-400">
                Connect your friend's laptop running Docker to test real live container metrics and auto-scaling.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </FullScreenLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CommonGridShape from '@/components/common/CommonGridShape.vue'
import FullScreenLayout from '@/components/layout/FullScreenLayout.vue'
import { useFinOps } from '@/composables/useFinOps'

const router = useRouter()
const { login, loginWithSupabase } = useFinOps()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isSubmitting = ref(false)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const fillSuperAdmin = () => {
  email.value = 'admin@smartcloud.com'
  password.value = 'Admin@123'
}

const handleSubmit = async () => {
  isSubmitting.value = true
  try {
    const trimmedEmail = email.value.trim().toLowerCase()

    // 1. Authenticate with Supabase Auth cloud credentials
    const res = await loginWithSupabase(email.value, password.value)
    if (res.success) {
      router.push('/')
      return
    }

    // 2. Demo fallback if user specifically entered demo keywords and Supabase auth wasn't used
    if (trimmedEmail.includes('northwind')) {
      await login('cust-northwind')
      router.push('/')
    } else if (trimmedEmail.includes('contoso')) {
      await login('cust-contoso')
      router.push('/')
    } else if (trimmedEmail.includes('fabrikam')) {
      await login('cust-fabrikam')
      router.push('/')
    } else if (trimmedEmail.includes('docker') || trimmedEmail.includes('friend')) {
      await login('cust-docker')
      router.push('/')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
