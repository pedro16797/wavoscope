import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      // Pragmatic policy so lint can be a required gate without a large
      // type-tightening pass. These stay visible as warnings and can be
      // promoted to errors later.
      '@typescript-eslint/no-explicit-any': 'warn',
      // Allow the destructure-to-omit pattern (`const { a, ...rest } = obj`)
      // and intentional `_`-prefixed throwaways.
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        ignoreRestSiblings: true,
      }],
      // React Compiler advisories (eslint-plugin-react-hooks v7) — not yet
      // adopted; keep as warnings rather than blocking.
      'react-hooks/preserve-manual-memoization': 'warn',
      'react-hooks/set-state-in-effect': 'warn',
    },
  },
])
