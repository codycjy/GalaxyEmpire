import { Table, Input, Select } from "antd";
import { useEffect, useState } from "react";

const { Search } = Input;

const columns = [
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

const App = () => {
  const [fullData, setFullData] = useState([]);
  const [displayData, setDisplayData] = useState([]);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });
  const [server, setServer] = useState("ze"); 
  const [serverList, setServerList] = useState([]);

  useEffect(() => {
    fetch('http://localhost:9000/api/scan/server')
      .then(response => response.json())
      .then(data => {
        const servers = data.map(server => ({ value: server, label: server }));
        setServerList(servers);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }, []);

  const onSearch = (value) => {
    fetch("http://localhost:9000/api/scan/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: value,
        server: server,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const newData = data.map((item) => ({ key: item.id, ...item }));
        setFullData(newData);
        setPagination({ ...pagination, total: newData.length });
        setDisplayData(newData.slice(0, pagination.pageSize));
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  const handleChange = (value) => {
    setServer(value);
  };

  const onChange = (pagination, filters, sorter, extra) => {
    const { current, pageSize } = pagination;
    const start = (current - 1) * pageSize;
    const end = start + pageSize;
    let processedData = [...fullData];
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
        defaultValue={server}
        style={{ width: 120 }}
        onChange={handleChange}
        options={serverList}
      />
      <Search
        placeholder="input search text"
        onSearch={onSearch}
        style={{ width: 200 }}
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
