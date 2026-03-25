vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.clipboard = "unnamedplus"
vim.opt.termguicolors = true
vim.opt.listchars = { space = '·', tab = '>-', trail = '-', nbsp = '%' }
vim.opt.list = true
vim.api.nvim_create_autocmd("BufWritePre", {
  pattern = "*",
  callback = function()
    local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)
    local changed = false
    for i, line in ipairs(lines) do
      local trimmed = line:gsub("%s+$", ""):gsub("\r", "")
      if trimmed ~= line then
        lines[i] = trimmed
        changed = true
      end
    end
    if changed then
      vim.api.nvim_buf_set_lines(0, 0, -1, false, lines)
    end
  end,
})
vim.opt.fixendofline = true
vim.opt.endofline = true
