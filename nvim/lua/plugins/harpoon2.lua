return {
  "ThePrimeagen/harpoon",
  branch = "harpoon2",
  dependencies = { "nvim-lua/plenary.nvim" },
  config = function()
    local harpoon = require("harpoon")
    harpoon:setup()

    -- Basic Keymaps
    local map = vim.keymap.set

    -- Add current file to Harpoon
    map("n", "<leader>a", function() harpoon:list():add() end, { desc = "Harpoon Add" })
    
    -- Toggle the visual menu
    map("n", "<C-e>", function() harpoon.ui:toggle_quick_menu(harpoon:list()) end, { desc = "Harpoon Menu" })

    -- Fast Jumping (using Alt keys for Windows Terminal compatibility)
    map("n", "<M-1>", function() harpoon:list():select(1) end)
    map("n", "<M-2>", function() harpoon:list():select(2) end)
    map("n", "<M-3>", function() harpoon:list():select(3) end)
    map("n", "<M-4>", function() harpoon:list():select(4) end)

    -- Toggle previous & next buffers stored within Harpoon list
    map("n", "<C-S-P>", function() harpoon:list():prev() end)
    map("n", "<C-S-N>", function() harpoon:list():next() end)
  end,
}
