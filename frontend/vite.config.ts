import react from "@vitejs/plugin-react";


export default defineConfig({
  plugins: [react()],

//追加コード
  server: {
    host: true, // true に設定すると、LAN やパブリックアドレスを含むすべてのアドレスをリッスン
    port: 5173, // 開発サーバーが使用するポート番号
  },
});