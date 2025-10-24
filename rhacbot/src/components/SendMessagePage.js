import React, { useState } from 'react';
import {
  Form,
  Input,
  Button,
  Upload,
  TreeSelect,
  Typography,
  message,
  Alert,
  Modal,
} from 'antd';
import { PlusOutlined  } from '@ant-design/icons';
import { sendMessage, authenticate } from '../api';
import buildings from '../buildings.json'; // Import the buildings data

const { Title } = Typography;
const { TextArea } = Input;

function SendMessagePage() {
  const [form] = Form.useForm();
  const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [selectedValues, setSelectedValues] = useState([]);
  const [file, setFile] = useState(null); // Track selected file
  const [preview, setPreview] = useState(''); // Track preview URL
    const [sendSummary, setSendSummary] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);

  // Organize buildings by region
  const buildingsByRegion = buildings.reduce((acc, building) => {
    const region = building.region;
    if (!acc[region]) {
      acc[region] = [];
    }
    acc[region].push(building);
    return acc;
  }, {});

  // Generate tree data for TreeSelect
  const treeData = Object.entries(buildingsByRegion).map(([regionName, regionBuildings]) => ({
    title: regionName,
    value: `region-${regionName}`,
    selectable: true,
    children: regionBuildings.map((building) => ({
      title: building.name,
      value: building.id.toString(),
    })),
  }));

  treeData.unshift({
    title: 'All Regions',
    value: 'region-all',
    selectable: true,
  });

  const handleLogin = async (values) => {
    const { password } = values;
    try {
      const res = await authenticate(password);
      if (res.status === 200) {
        setAuthenticated(true);
      }
    } catch (err) {
      message.error('Incorrect password');
    }
  };

  const handleFileChange = ({ fileList }) => {
    if (fileList.length > 0) {
      const latestFile = fileList[fileList.length - 1].originFileObj;
      setFile(latestFile);
      setPreview(URL.createObjectURL(latestFile)); // Generate preview URL
    } else {
      setFile(null);
      setPreview('');
    }
  };

  const handleSubmit = async (values) => {
    const { message_body } = values;

  const formData = new FormData();
  formData.append('password', password);
  formData.append('message_body', message_body);
    if (file) {
      formData.append('image_file', file);
    }

    const regions = [];
    const buildingIds = [];

    selectedValues.forEach((valueObj) => {
      const value = valueObj.value || valueObj;
      const strValue = String(value);
      if (strValue.startsWith('region-')) {
        regions.push(strValue.replace('region-', ''));
      } else {
        buildingIds.push(strValue);
      }
    });

    if (regions.length > 0) {
      if (regions.includes('all')) {
        formData.append('regions', 'all');
      } else {
        regions.forEach((region) => formData.append('regions', region));
      }
    }

    if (buildingIds.length > 0) {
      buildingIds.forEach((id) => formData.append('building_ids', id));
    }

    if (regions.length === 0 && buildingIds.length === 0) {
      message.error('Please select at least one region or building');
      return;
    }

    try {
      const response = await sendMessage(formData);
        // Handle backend response with possible partial failures
        const data = response.data || {};
        if (response.status === 200) {
          message.success(data.message || 'Messages sent successfully');
          setSendSummary(null);
        } else if (response.status === 207) {
          // Partial success
          setSendSummary(data);
          message.warning(data.message || 'Some messages failed');
        } else {
          setSendSummary(data);
          message.error(data.message || 'Failed to send messages');
        }
      form.resetFields();
      setSelectedValues([]);
      setFile(null);
      setPreview('');
    } catch (error) {
      message.error('Error sending message');
    }
  };

  if (!authenticated) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <div
          style={{
            maxWidth: '60vw',
            width: '100%',
            margin: '0 auto',
            padding: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderRadius: '15px',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
          }}
        >
          <div style={{ maxWidth: 400, margin: '0 auto', padding: '20px' }}>
            <Title level={3} style={{ textAlign: 'center' }}>
              Executive Login
            </Title>
            <Form onFinish={handleLogin} autoComplete="off">
              <Form.Item
                name="password"
                rules={[{ required: true, message: 'Please input your password' }]}
              >
                <Input.Password autoComplete="current-password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" block>
                  Login
                </Button>
              </Form.Item>
            </Form>
          </div>
        </div>
      </div>
    );
  }

  const uploadButton = (
    <button style={{ border: 0, background: 'none' }} type="button">
        <PlusOutlined />
      <div style={{ marginTop: 8 }}>Upload</div>
    </button>
  );

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
      }}
    >
      <div
        style={{
          maxWidth: '60vw',
          width: '100%',
          margin: '0 auto',
          padding: '20px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: '15px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
        }}
      >
        {sendSummary && (
          <div style={{ marginBottom: 12 }}>
            <Alert
              message={sendSummary.message}
              description={
                sendSummary.summary
                  ? `Sent ${sendSummary.summary.sent}/${sendSummary.summary.total} — ${sendSummary.summary.failed} failed`
                  : null
              }
              type={sendSummary.summary ? 'warning' : 'error'}
              showIcon
              action={
                sendSummary.failures ? (
                  <Button size="small" onClick={() => setModalOpen(true)}>
                    Details
                  </Button>
                ) : null
              }
            />
          </div>
        )}

        <Modal
          title="Send failures"
          open={modalOpen}
          onCancel={() => setModalOpen(false)}
          footer={<Button onClick={() => setModalOpen(false)}>Close</Button>}
        >
          {sendSummary && sendSummary.failures ? (
            <div style={{ maxHeight: 300, overflowY: 'auto' }}>
              {sendSummary.failures.map((f) => (
                <div key={f.group_id} style={{ marginBottom: 8 }}>
                  <strong>Group {f.group_id}:</strong>
                  <div>{f.error || 'Unknown error'}</div>
                </div>
              ))}
            </div>
          ) : (
            <div>No failure details available.</div>
          )}
        </Modal>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            // minHeight: '60vh', // Adjust height to center content vertically
          }}
        >
          <Title level={3} style={{ textAlign: 'center' }}>
            Send Message
          </Title>
          <Form form={form} onFinish={handleSubmit} autoComplete="off">
            <Form.Item
              name="message_body"
              rules={[{ required: true, message: 'Please input the message body' }]}
            >
              <TextArea rows={4} placeholder="Message Body" />
            </Form.Item>
            <Form.Item>
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <Upload
                  beforeUpload={() => false}
                  listType="picture-card"
                  className="avatar-uploader"
                  onChange={handleFileChange}
                  accept="image/*"
                  maxCount={1}
                  showUploadList={false}
                >
                  {preview ? <img src={preview} alt="avatar" style={{ width: '100%' }} /> : uploadButton}
          
                </Upload>
              </div>
            </Form.Item>
            <Form.Item>
              <TreeSelect
                treeData={treeData}
                value={selectedValues}
                onChange={(value) => setSelectedValues(value)}
                treeCheckable={true}
                showCheckedStrategy={TreeSelect.SHOW_PARENT}
                placeholder="Please select regions or buildings"
                style={{ width: '100%' }}
                allowClear
                treeDefaultExpandAll
                treeCheckStrictly={true}
                labelInValue
              />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" block>
                Send Message
              </Button>
            </Form.Item>
          </Form>
        </div>
      </div>
    </div>
  );
}

export default SendMessagePage;
