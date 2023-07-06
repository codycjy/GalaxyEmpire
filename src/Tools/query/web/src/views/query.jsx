import { Table } from "antd";
import { AudioOutlined } from "@ant-design/icons";
import { Input, Space, Select } from "antd";
import { useState } from "react";
const { Search } = Input;
const columns = [
  // {
  //   title: 'Server',
  //   dataIndex: 'server',
  //   onFilter: (value, record) => record.server.includes(value),
  //   sorter: (a, b) => a.server.localeCompare(b.server),
  // },
  {
    title: "Name",
    dataIndex: "name",
    onFilter: (value, record) => record.name.includes(value),
    sorter: (a, b) => a.name.localeCompare(b.name),
  },
  {
    title: "Position",
    dataIndex: "pos",
    onFilter: (value, record) => record.pos.includes(value),
    sorter: (a, b) => a.pos.localeCompare(b.pos),
  },
  {
    title: "Crystal",
    dataIndex: "crystal",
    defaultSortOrder: "descend",
    sorter: (a, b) => a.crystal - b.crystal,
  },
  {
    title: "Metal",
    dataIndex: "metal",
    defaultSortOrder: "descend",
    sorter: (a, b) => a.metal - b.metal,
  },
  {
    title: "Has Ally",
    dataIndex: "has_ally",
    filters: [
      { text: "Yes", value: 1 },
      { text: "No", value: 0 },
    ],
    onFilter: (value, record) => record.has_ally === value,
  },
  {
    title: "Ally Name",
    dataIndex: "ally_name",
    onFilter: (value, record) => record.ally_name.includes(value),
    sorter: (a, b) => a.ally_name.localeCompare(b.ally_name),
  },
];

// Assuming that `data` is an array of records:

const handleChange = (req) => console.log(req);

const App = () => {
  const [fullData, setFullData] = useState([]);
  const [displayData, setDisplayData] = useState([]);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });
  const [server, setServer] = useState("ze"); // Initial server value

  const onSearch = (value) => {
    fetch("http://localhost:5173/api/scan/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: value,
        server: server, // Use server state variable
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const newData = data.map((item) => ({ key: item.id, ...item }));
        setFullData(newData);
        setPagination({ ...pagination, total: newData.length });
        setDisplayData(newData.slice(0, pagination.pageSize)); // 初始化显示数据
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const handleChange = (value) => {
    setServer(value); // Update server value when select option changes
  };

  const onChange = (pagination, filters, sorter, extra) => {
    const { current, pageSize } = pagination;
    const start = (current - 1) * pageSize;
    const end = start + pageSize;
    let processedData = [...fullData]; // Use a copy of full data to perform operations
    if (sorter.order) {
      processedData =
        sorter.order === "ascend"
          ? processedData.sort((a, b) => a[sorter.field] - b[sorter.field])
          : processedData.sort((a, b) => b[sorter.field] - a[sorter.field]);
    }
    setPagination({ ...pagination });
    setDisplayData(processedData.slice(start, end));
  };

  return (
    <>
      <Select
        defaultValue="ze"
        style={{ width: 120 }}
        onChange={handleChange}
        options={[
          { value: "ze", label: "ze" },
          { value: "g10", label: "g10" },
        ]}
      />
      <Search
        placeholder="input search text"
        onSearch={onSearch}
        style={{
          width: 200,
        }}
      />

      <Table
        columns={columns}
        dataSource={displayData}
        pagination={pagination}
        onChange={onChange}
      />
    </>
  );
};
export default App;
