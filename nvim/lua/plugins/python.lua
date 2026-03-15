return {
  -- 1. AUTOCOMPLETE
  {
    'saghen/blink.cmp',
    version = '*',
    opts = {
    keymap = { 
	preset = 'none',
	['<C-k>'] = { 'select_prev', 'fallback' },
	['<C-j>'] = { 'select_next', 'fallback' },
	['<Tab>'] = { 'accept', 'fallback' },
	['<C-y>'] = { 'accept', 'fallback' }, -- keeping it since you're used to it
	['<C-space>'] = { 'show', 'fallback' }, -- manually trigger completion
	['<C-e>'] = { 'cancel', 'fallback' },
	},
      appearance = {
        nerd_font_variant = 'mono'
      },
      sources = {
        default = { 'lsp', 'path', 'snippets', 'buffer' },
      },
    },
  },

-- 2. LSP
  {
    "neovim/nvim-lspconfig", -- still needed as plugin for now, but we use new API
    dependencies = { "saghen/blink.cmp" },
    config = function()
      local capabilities = require('blink.cmp').get_lsp_capabilities()

      -- Disable Ruff's hover in favor of Pyright
      vim.api.nvim_create_autocmd("LspAttach", {
        group = vim.api.nvim_create_augroup('lsp_attach_disable_ruff_hover', { clear = true }),
        callback = function(args)
          local client = vim.lsp.get_client_by_id(args.data.client_id)
          if client and client.name == 'ruff' then
            client.server_capabilities.hoverProvider = false
          end
        end,
      })

      -- PYRIGHT
      vim.lsp.config('pyright', {
        capabilities = capabilities,
	position_encoding = "utf-16",
        settings = {
          pyright = { disableOrganizeImports = true },
          python = {
            analysis = {
              typeCheckingMode = "basic",
              autoSearchPaths = true,
	      diagnosticMode = "openFilesOnly",
            }
          }
        }
      })
      vim.lsp.enable('pyright')

      -- RUFF
      vim.lsp.config('ruff', {
	capabilities = capabilities,
	position_encoding = "utf-16",
      })
      vim.lsp.enable('ruff')

      -- FORMAT + ORGANIZE IMPORTS ON SAVE
      vim.api.nvim_create_autocmd("BufWritePre", {
        pattern = "*.py",
        callback = function()
	vim.lsp.buf.code_action({ 
	context = { only = { "source.organizeImports" } }, 
	apply = true,
	})
	vim.lsp.buf.format({ async = false, name = "ruff" })
        end,
      })
    end,
  },
  -- Tree sitter
  {
    'nvim-treesitter/nvim-treesitter',
    lazy = false,
    build = ':TSUpdate',
    init = function()
        require('nvim-treesitter').install({ 'python', 'lua', 'vim', 'vimdoc' , 'markdown', 'markdown_inline'})

        vim.api.nvim_create_autocmd('FileType', {
          pattern = { 'python' },
          callback = function() vim.treesitter.start() end,
    })
    end,
  },
}
