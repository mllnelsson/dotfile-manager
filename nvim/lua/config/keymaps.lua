local map = vim.keymap.set

map('n', '<C-p>', '<C-^>', { desc = "Toggle Last File (The Back Button)" })
map('i', 'jj', '<Esc>', { desc = "Fast Escape" })
map("n", "-", "<CMD>Oil<CR>", { desc = "Open Parent Directory" })
vim.keymap.set("n", "<leader>w", "<cmd>w<cr>", { desc = "Save File" })
vim.keymap.set("n", "<leader>W", "<cmd>wa<cr>", { desc = "Save All Buffers" })
