import React from 'react';

const ContentStatisticsCard = ({ icon, title, value, description }) => {
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <div className="flex items-center mb-2">
        <div className="mr-2">
          {icon}
        </div>
        <h2 className="text-lg font-medium text-gray-700">{title}</h2>
      </div>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
    </div>
  );
};

export default ContentStatisticsCard;