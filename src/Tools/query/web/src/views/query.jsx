import { Table, Input, Select } from "antd";
import { useEffect, useState } from "react";

const { Search } = Input;

const columns = [
  {
    title: "用户名",
    dataIndex: "name",
    onFilter: (value, record) => record.name.includes(value),
    sorter: (a, b) => a.name.localeCompare(b.name),
  },
  {
    title: "位置",
    dataIndex: "pos",
    onFilter: (value, record) => record.pos.includes(value),
    sorter: (a, b) => a.pos.localeCompare(b.pos),
  },
  {
    title: "水晶废墟",
    dataIndex: "crystal",
    defaultSortOrder: "descend",
    sorter: (a, b) => a.crystal - b.crystal,
  },
  {
    title: "金属废墟",
    dataIndex: "metal",
    defaultSortOrder: "descend",
    sorter: (a, b) => a.metal - b.metal,
  },
  {
    title: "拥有联盟",
    dataIndex: "has_ally",
    filters: [
      { text: "Yes", value: 1 },
      { text: "No", value: 0 },
    ],
    onFilter: (value, record) => record.has_ally === value,
    render: (has_ally) => has_ally === 1 ? '是' : '否'
  },
  {
    title: "联盟名称",
    dataIndex: "ally_name",
    onFilter: (value, record) => record.ally_name.includes(value),
    sorter: (a, b) => a.ally_name.localeCompare(b.ally_name),
  },
];

const App = () => {
  const [fullData, setFullData] = useState([]);
  const [displayData, setDisplayData] = useState([]);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 });
  const [server, setServer] = useState("ze"); 
  const [serverList, setServerList] = useState([]);
  const [lastModified, setLastModified] = useState('');

  useEffect(() => {
    fetch(`http://localhost:9000/api/scan/status/${server}`)
      .then(response => response.json())
      .then(data => {
        setLastModified(data.last_modified);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, [server]); 
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
    let processedData = [...fullData];
    
    if (sorter.order) {
      processedData =
        sorter.order === "ascend"
          ? processedData.sort((a, b) => {
              if (typeof a[sorter.field] === "string") {
                return a[sorter.field].localeCompare(b[sorter.field]);
              }
              return a[sorter.field] - b[sorter.field];
            })
          : processedData.sort((a, b) => {
              if (typeof b[sorter.field] === "string") {
                return b[sorter.field].localeCompare(a[sorter.field]);
              }
              return b[sorter.field] - a[sorter.field];
            });
    }

    const start = (current - 1) * pageSize;
    const end = start + pageSize;
    setPagination({ ...pagination });
    setFullData(processedData); // set the sorted data as fullData
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
      <div>最后更新时间: {lastModified}</div>
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
