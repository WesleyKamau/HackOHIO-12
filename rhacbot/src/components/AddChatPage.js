import React, { useState } from 'react';
import { addChat } from '../api';
import {
  Form,
  Input,
  Button,
  Select,
  Typography,
  message,
} from 'antd';
import buildings from '../buildings.json'; // Import the buildings data

const { Title } = Typography;
const { Option } = Select;

function AddChatPage() {
  const [form] = Form.useForm();
  const [buildingId, setBuildingId] = useState('');
  const [floorNumber, setFloorNumber] = useState('');
  const [groupmeLink, setGroupmeLink] = useState('');

  const handleSubmit = async (values) => {
    const data = {
      groupme_link: values.groupme_link,
      building_id: parseInt(values.building_id),
      floor_number: parseInt(values.floor_number),
    };

    try {
      const response = await addChat(data);
      message.success(response.data.message);
      // Reset form
      form.resetFields();
    } catch (error) {
      console.error(error);
      message.error('Error adding chat');
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh', // Full viewport height
      }}
    >
      <div
        style={{
          maxWidth: '60vw',
          width: '100%',
          margin: '0 auto', // Center horizontally
          padding: '20px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)', // Opaque white background
          borderRadius: '15px', // Curved edges
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)', // Optional shadow for depth
        }}
      >
        <Title level={3} style={{ textAlign: 'center' }}>
          Add RHACbot to your GroupMe!
        </Title>
        <Form form={form} onFinish={handleSubmit}>
          <Form.Item
            name="groupme_link"
            rules={[{ required: true, message: 'Please input the GroupMe Invite Link' }]}
          >
            <Input
              placeholder="GroupMe Invite Link"
              value={groupmeLink}
              onChange={(e) => setGroupmeLink(e.target.value)}
            />
          </Form.Item>
          <Form.Item
            name="building_id"
            rules={[{ required: true, message: 'Please select your building' }]}
          >
            <Select
              placeholder="Select Building"
              value={buildingId}
              onChange={(value) => setBuildingId(value)}
              showSearch
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().includes(input.toLowerCase())
              }
            >
              {buildings.map((building) => (
                <Option key={building.id} value={building.id}>
                  {building.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="floor_number"
            rules={[{ required: true, message: 'Please input your floor number' }]}
          >
            <Input
              type="number"
              placeholder="Floor Number"
              value={floorNumber}
              onChange={(e) => setFloorNumber(e.target.value)}
            />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Add Chat
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
}

export default AddChatPage;
