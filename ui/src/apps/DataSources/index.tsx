import React from 'react';
import { DocumentIngest } from '../../components/DocumentIngest';

interface Props {
    onUpload: (file: File, type: string) => Promise<void>;
    isLoading: boolean;
}

export const DataSources: React.FC<Props> = ({ onUpload, isLoading }) => {
    return (
        <div className="h-full w-full overflow-hidden relative">
            <DocumentIngest onUpload={onUpload} isLoading={isLoading} />
        </div>
    );
};
