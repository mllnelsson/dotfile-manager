local map = vim.keymap.set

map('n', '<C-p>', '<C-^>', { desc = "Toggle Last File (The Back Button)" })
map('i', 'jj', '<Esc>', { desc = "Fast Escape" })
map("n", "-", "<CMD>Oil<CR>", { desc = "Open Parent Directory" })
map("n", "<leader>w", "<cmd>w<cr>", { desc = "Save File" })
map("n", "<leader>W", "<cmd>wa<cr>", { desc = "Save All Buffers" })
map("n", "<C-h>", "<C-w><C-h>", { desc = "Move left" })
map("n", "<C-j>", "<C-w><C-j>", { desc = "Move down" })
map("n", "<C-k>", "<C-w><C-k>", { desc = "Move up" })
map("n", "<C-l>", "<C-w><C-l>", { desc = "Move right" })
map("n", "<leader>t", function() Snacks.terminal() end, { desc = "Toggle Terminal" })
