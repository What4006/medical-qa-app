# 项目 Git 使用规范

## 一、首次获取项目

1.  **克隆仓库 (Clone)**
    在你自己的电脑上找一个合适的文件夹，执行以下命令，将远程仓库克隆到本地。这个操作对于每个成员来说，只需要做一次。
    ```bash
    git clone [https://github.com/What4006/medical-qa-app.git](https://github.com/What4006/medical-qa-app.git)
    ```
    *在 `clone` 的过程中，Git 会自动将远程仓库地址保存为别名 `origin`。*

## 二、日常开发流程

这是一个标准的开发循环，请在每次写代码时都遵循这个顺序。

1.  **编写代码前：拉取最新代码 (Pull)**
    ```bash
    git pull origin master
    ```

2.  **检查当前状态 (Status)**
    可以随时告诉你哪些文件被修改了、哪些是新增的。
    ```bash
    git status
    ```

3.  **添加更改 (Add)**
    当你修改完一部分代码后，使用此命令将所有更改添加到暂存区。
    ```bash
    git add .
    ```

4.  **提交更改 (Commit)**
    为你的修改创建一个本地的“存档点”，并写清楚本次修改的内容。
    ```bash
    git commit -m "类型: 修改内容的简述"
    ```
    **建议的类型 (type) 包括：**
    * `feat`: 新功能
    * `fix`: 修复 bug
    * `docs`: 修改文档
    * `style`: 修改代码格式
    * *示例: `git commit -m "fix: 修复用户无法登录的问题"`*

5.  **推送至远程仓库 (Push)**
    将你本地的所有新提交上传到 GitHub。
    ```bash
    git push origin master
    ```

## 三、常见问题

* **执行 `git commit` 时卡在编辑器里怎么办？**
    * 如果进入了 Vim 编辑器，按 `Esc` 键，然后输入 `:wq` 再按回车即可保存退出。