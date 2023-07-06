import { SearchOutlined, UploadOutlined, UserOutlined, VideoCameraOutlined } from '@ant-design/icons';
import { Layout, Menu, theme } from 'antd';
import React from 'react';
import { Outlet } from 'react-router-dom';
import { NavLink } from 'react-router-dom';

const { Header, Content, Footer, Sider } = Layout;
const App = () => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();
  const labelArray=["Query"]
  return (
    <Layout style={{minHeight:"100vh"}}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        onBreakpoint={(broken) => {
          // console.log(broken);
        }}
        onCollapse={(collapsed, type) => {
          console.log(collapsed, type);
        }}
      >
        <div className="demo-logo-vertical" />
        
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']}>
  {[
    { icon: SearchOutlined, label: "Query", path: "/query" },
    // ... add more items here
  ].map((item, index) => (
    <Menu.Item key={String(index + 1)} icon={React.createElement(item.icon)}>
      <NavLink to={item.path}>{item.label}</NavLink>
    </Menu.Item>
  ))}
</Menu>

      </Sider>
      <Layout>
        <Header
          style={{
            padding: 0,
            background: colorBgContainer,
          }}
        />
        <Content
          style={{
            margin: '24px 16px 0',
          }}
        >
          <div
            style={{
              padding: 24,
              minHeight: "80vh",
              background: colorBgContainer,
            }}
          >
            <Outlet/>
          </div>
        </Content>
        <Footer
          style={{
            textAlign: 'center',
          }}
        >
          Ant Design ©2023 Created by Ant UED
        </Footer>
      </Layout>
    </Layout>
  );
};
export default App;